import datetime


class PUUser:
    """
    PUUser object to store user data
    """

    def __init__(self):
        # from /api/sessions
        self.session_id: str = None
        self.session_token: str = None
        self.session_created: datetime.datetime = None
        self.session_expiry: datetime.datetime = None
        self.session_last_activity: datetime.datetime = None
        self.session_termination: datetime.datetime = None
        self.session_account_disposable_id: str = None

        self.account_id: str = None
        self.display_name: str = None
        self.email: str = None
        self.preferred_language: str = None
        self.registered: datetime.datetime = None
        self.confirmed: datetime.datetime = None
        self.confirmation_source: str = None
        self.deleted: datetime.datetime = None
        self.delete_reason: str = None
        self.roles: list[str] = None
        self.coupon: str = None

        # from /api/users/{pu_id}
        self.pu_id: str = None
        self.user_disposable_id: str = None
        self.early_access_support_tier: str = None
        self.perks: list[str] = None
        self.subscription_level: str = None
        self.subscription_expiry: datetime.datetime = None
        self.first_access_game_time_months_left: int = None

        # raw json data
        self._session_response_data: dict = None
        self._user_response_data: dict = None

    def update_from_session_response(self, data: dict):
        """
        updates the PUUser object with data from the /api/sessions response
        """
        _dt = self.__convert_to_datetime
        self.session_id = data["id"]
        self.session_token = data["token"]
        self.session_created = _dt(data["created"])
        self.session_expiry = _dt(data["expiry"])
        self.session_last_activity = _dt(data["lastActivity"])
        self.session_termination = _dt(data["termination"])
        self.session_account_disposable_id = data["account"]["disposableId"]

        self.account_id = data["account"]["id"]
        self.display_name = data["account"]["displayName"]
        self.email = data["account"]["email"]
        self.preferred_language = data["account"]["preferredLanguage"]
        self.registered = _dt(data["account"]["registered"])
        self.confirmed = _dt(data["account"]["confirmed"])
        self.confirmation_source = data["account"]["confirmationSource"]
        self.deleted = data["account"]["deleted"]
        self.delete_reason = data["account"]["deleteReason"]
        self.roles = data["account"]["roles"]
        self.coupon = data["account"]["coupon"]

        self.pu_id = data["account"]["userIds"]["pu"]

        self._session_response_data = data

    def update_from_user_response(self, data: dict):
        """
        updates the PUUser object with data from the /api/users/{pu_id} response
        """
        _dt = self.__convert_to_datetime
        self.pu_id = data["id"]
        self.user_disposable_id = data["disposableId"]
        self.account_id = data["accountId"]
        self.registered = _dt(data["creation"])
        self.early_access_support_tier = data["highestTier"]
        self.perks = data["perks"]
        self.subscription_level = data["subscription"]["level"]
        self.subscription_expiry = data["subscription"]["expiry"]
        self.first_access_game_time_months_left = data["firstAccessGameTimeMonthsLeft"]

        self._user_response_data = data

    def __convert_to_datetime(self, data: str) -> datetime.datetime:
        if data is None or data == "":
            return None
        return datetime.datetime.fromisoformat(data)

    def __str__(self):
        return f"PUUser({self.display_name} | {self.subscription_level})"
