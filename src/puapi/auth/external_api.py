"""
This module contains the `ExternalApiAuthProvider` class which is used to
authenticate users
"""

import datetime
import json
import logging
from typing import Any
from urllib.parse import urljoin

import requests

from puapi.auth.crypto import time_signature
from puapi.auth.marker import AuthProviderMarker
from puapi.models.pu_user import PUUser
from puapi.util.decorators import retry_on_exception
from puapi.util.url_helpers import encode_url_params


class ExternalApiAuthProvider(AuthProviderMarker):
    """
    ExternalApiAuthProvider class to authenticate user and get user data using
    the Prosperous Universe Internal API

    Example:
    ```python
    api = ExternalApiAuthProvider(email, password)
    user = api.login()
    cookies = api.cookies
    still_logged_in = api.check_auth()
    ```
    """

    def __init__(
        self,
        *,  # enforce keyword-only arguments
        email,
        password,
        session: requests.Session | None = None,
        retries: int = 3,
        retry_delay: int = 3,
        request_timeout: int = 10,
    ):
        self.email = email
        self.password = password
        self._session = session or requests.Session()
        self._retries = retries
        self._retry_delay = retry_delay
        self._request_timeout = request_timeout

        self.pu_user = PUUser()
        self._logger = logging.getLogger(f"puapi.{self.__class__.__name__}")
        self.cookies: list[dict[str, Any]] = []

        self._auth_session_url = "https://sar.simulogics.games/api/sessions/"
        self._auth_user_url = "https://sar.simulogics.games/api/pu/users/"
        self._auth_shared_headers = {
            "accept": "*/*",
            "accept-language": "en",
            "dnt": "1",
            "origin": "https://prosperousuniverse.com",
            "sec-ch-ua": '"Chromium";v="123", "Not:A-Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"macOS"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "cross-site",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) \
            AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 \
                Safari/537.36",
        }

    def update_cookies(self, cookies: list[dict[str, Any]]):
        """
        for each cookie in cookies, if cookie with the same name exists, update
        it else add it to self.cookies list

        ```python
        cookies = [
            {
                "name": "cookie_name",
                "value": "cookie_value",
                "domain": ".prosperousuniverse.com",
                "path": "/",
                "expires": datetime.datetime.now(datetime.UTC)
                + datetime.timedelta(days=1),
            }
        ]
        api.update_cookies(cookies)
        ```

        :param cookies: list of cookies to update
        """

        if not self.cookies:
            self.cookies = cookies
            return

        for cookie in cookies:
            for i, c in enumerate(self.cookies):
                if c["name"] == cookie["name"]:
                    self.cookies[i] = cookie
                    break
            else:
                self.cookies.append(cookie)

    def check_auth(self) -> bool:
        return True

    def get_user(self) -> PUUser:
        return self.pu_user

    def auth(self) -> PUUser:
        """
        authenticates user and updates PUUser object with data
        from /api/sessions and /api/users/{pu_id}

        ```python
        api = ExternalApiAuthProvider(email, password)
        user = api.auth()
        ```

        :return: PUUser object
        """

        def on_error(e: Exception):
            self._logger.error(
                "%s error occurred while trying to login: %s",
                e.__class__.__name__,
                str(e),
            )

        retry = retry_on_exception(
            retries=self._retries,
            retry_delay=self._retry_delay,
            catch=(
                requests.JSONDecodeError,
                requests.RequestException,
            ),
            on_error_callback=on_error,
        )

        # auth session and user api calls
        session_res = retry(self.__get_api_session)(self.email, self.password)
        self.pu_user.update_from_session_response(session_res)

        user_res = retry(self.__get_api_user)(self.pu_user.pu_id)
        self.pu_user.update_from_user_response(user_res)

        ingress_cookie = retry(self.__get_ingress_cookie)()

        # add cookies to session
        cookies: list[dict[str, Any]] = [
            {
                "name": "cookie_consent",
                "value": "accepted",
                "domain": ".prosperousuniverse.com",
                "path": "/",
                "expires": datetime.datetime.now(datetime.UTC)
                + datetime.timedelta(days=(365 + 30 + 5), hours=12),
            },
            {
                "name": "pu-id",
                "value": self.pu_user.session_token,
                "domain": ".prosperousuniverse.com",
                "path": "/",
                "expires": datetime.datetime.now(datetime.UTC)
                + datetime.timedelta(hours=12),
            },
            {
                "name": "INGRESSCOOKIE",
                "value": ingress_cookie,
                "domain": "apex.prosperousuniverse.com",
                "path": "/",
                "expires": datetime.datetime.now(datetime.UTC)
                + datetime.timedelta(days=365),  # it's a session cookie
            },
        ]

        for cookie in cookies:
            self._session.cookies.set(
                cookie["name"],
                cookie["value"],
                domain=cookie["domain"],
                path=cookie["path"],
                expires=cookie["expires"].timestamp(),
            )

        self.update_cookies(cookies)

        return self.pu_user

    def __get_api_session(self, email: str, password: str) -> dict[str, Any]:
        self._logger.debug("authenticating user %s", email)
        res = self._session.post(
            self._auth_session_url,
            headers={
                **self._auth_shared_headers,
                "content-type": "application/json",
                "referer": "https://prosperousuniverse.com/auth/login",
            },
            data=json.dumps(
                {
                    "login": email,
                    "password": password,
                    "persistent": True,
                    "method": "password",
                    "brand": "pu",
                    "metadata": {
                        "landingPage": "https://prosperousuniverse.com/"
                    },
                }
            ),
            timeout=self._request_timeout,
        )
        res.raise_for_status()
        return res.json()

    def __get_api_user(self, pu_user_id: str) -> dict[str, Any]:
        self._logger.debug("getting user data for %s", self.email)
        res = self._session.get(
            urljoin(self._auth_user_url, pu_user_id),
            timeout=self._request_timeout,
            headers={
                **self._auth_shared_headers,
                "authorization": f"Bearer {self.pu_user.session_token}",
                "referer": "https://prosperousuniverse.com/account",
            },
        )
        res.raise_for_status()
        return res.json()

    def __get_ingress_cookie(self) -> str | None:
        self._logger.debug("getting ingress cookie for %s", self.email)
        res = self._session.get(
            "https://apex.prosperousuniverse.com/",
            timeout=self._request_timeout,
            headers=self._auth_shared_headers,
            stream=False,
        )
        res.raise_for_status()
        print(res.cookies.get_dict().get("INGRESSCOOKIE"))
        return self._session.cookies.get_dict().get("INGRESSCOOKIE")

    def _get_sid(self) -> str:
        """
        Get the session id from the socket.io endpoint

        Used in following requests to the socket.io endpoint
        """
        res = self._session.get(
            encode_url_params(
                "https://apex.prosperousuniverse.com/socket.io/",
                {
                    "EIO": "4",
                    "transport": "polling",
                    "t": time_signature(),
                },
            ),
            headers={
                "accept": "*/*",
                "accept-language": "en",
                "dnt": "1",
                "referer": "https://apex.prosperousuniverse.com/",
                "user-agent": "Mozilla/5.0 \
                    (Macintosh; Intel Mac OS X 10_15_7) \
                        AppleWebKit/537.36 (KHTML, like Gecko) \
                        Chrome/123.0.0.0 Safari/537.36",
            },
        )
        res.raise_for_status()
        json_start_index = res.text.find("{")  # ignoring the encoded 0
        res_json = json.loads(res.text[json_start_index:])

        return res_json.get("sid")
