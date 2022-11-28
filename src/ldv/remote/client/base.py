from ldv.remote.auth.base import BaseAuth

class BaseClient:

    def __init__(self, auth: BaseAuth) -> None:
        self.client = None

    def validate_credentials(self) -> None:
        raise NotImplementedError()