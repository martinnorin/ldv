import configparser
import logging
import os

from ldv.constants.auth import AuthConstants as AC
from ldv.dto.auth import BaseAuthDto
from ldv.enums.auth import LdvRemoteProvider
from ldv.utils.exceptions import AuthReadError

# Create separate logger with file as name
logger = logging.getLogger(__name__)

class BaseAuth:

    _folder = ".ldv"
    _filename = "auth"

    def __init__(self, provider: LdvRemoteProvider) -> None:
        """Initialize instance. """

        self._remote_provider = provider

    def verify_authentication(self) -> None:
        raise NotImplementedError()

    @staticmethod
    def get_auth_path() -> str:
        return os.path.join(BaseAuth._folder, BaseAuth._filename)

    @staticmethod
    def get_base_auth_values() -> BaseAuthDto:
        try:
            auth = configparser.ConfigParser()
            auth.read(BaseAuth.get_auth_path())
        except Exception as e:
            logger.error("Error when reading auth")
            raise AuthReadError().with_traceback(e.__traceback__)

        # Try to find correct enum from string for provider
        try:
            # Must use .upper() to match with enum name
            # when parsing string to enum
            provider: LdvRemoteProvider = LdvRemoteProvider[
                auth[AC.PROVIDER][AC.NAME].upper()
            ]
        except Exception as e:
            logger.warning(f"Provider in auth file is incorrect. "
                           f"Using 'none' instead. '{repr(e)}'")
            provider = LdvRemoteProvider.NONE


        return BaseAuthDto(provider=provider)

    @staticmethod
    def get_auth_values() -> BaseAuthDto:
        raise NotImplementedError()
