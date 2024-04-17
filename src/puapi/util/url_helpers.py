"""
URL helper functions.
"""

from urllib.parse import urlencode, urlparse, urlunparse


def encode_url_params(base_url: str, params: dict[str, str]) -> str:
    """
    Encode a URL with parameters.

    Example:
    ```python
    url = "https://example.com"
    params = {
        "key1": "value1",
        "key2": "value2",
    }
    encoded_url = encode_url_params(url, params)
    print(encoded_url)
    ```
    ```plaintext
    >>> https://example.com?key1=value1&key2=value2
    ```

    :param base_url: The base URL to encode.
    :param params: The parameters to encode.
    """
    encoded_params = urlencode(params)
    parsed_url = urlparse(base_url)
    final_url = urlunparse(
        (
            parsed_url.scheme,
            parsed_url.netloc,
            parsed_url.path,
            parsed_url.params,
            encoded_params,
            parsed_url.fragment,
        )
    )

    return final_url
