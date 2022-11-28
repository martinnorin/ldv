import configparser
import logging
import os
from typing import Optional

import boto3

from ldv.constants.auth import AuthConstants as AC
from ldv.constants.auth import AwsAuthConstants as AAC
from ldv.constants.remote import RemoteStorageConstants as RSC
from ldv.dto.auth import AwsAuthDto
from ldv.enums.auth import AwsAuthType, LdvRemoteProvider
from ldv.remote.auth.base import BaseAuth
from ldv.utils.aws_config import AwsConfig
from ldv.utils.exceptions import (
    AWSS3NoNoCredentialsProvidedError,
    AuthReadError,
    InvalidAuthenticationTypeError,
    NoAuthenticationEnvironmentVariablesSetError,
    NoAuthenticationProfileFoundError
)

# Create separate logger with file as name
logger = logging.getLogger(__name__)

class AwsAuth(BaseAuth):

    def __init__(self) -> None:
        super().__init__(LdvRemoteProvider.AWS)

    def store_auth(
        self,
        profile_name: str = None,
        env_credentials: bool = None,
        region_name: str = None
    ) -> None:
        """Store authentication info in file

        Args:
            profile_name (str, optional): profile name.
            env_credentials (bool, optional): Use credentials stored in
                environment variables.
            region_name (str, optional): region name

        Raises:
            InvalidAuthenticationTypeError: if authentication type is not one
                of the valid values.
        """
        auth_type: Optional[AwsAuthType] = None
        if profile_name:
            auth_type = AwsAuthType.PROFILE
        elif env_credentials:
            auth_type = AwsAuthType.ENV_CREDENTIALS
        if not auth_type:
            raise InvalidAuthenticationTypeError(AwsAuthType.valid_values())

        if not os.path.exists(self._folder):
            os.mkdir(self._folder)

        auth = configparser.ConfigParser()
        auth[AC.PROVIDER] = {
            AC.NAME: LdvRemoteProvider.AWS.value
        }
        auth[AAC.AWS_AUTH] = {
            AAC.TYPE: auth_type.value,
            AAC.REGION_NAME: region_name or "",
            AAC.PROFILE_NAME: profile_name or ""
        }

        with open(BaseAuth.get_auth_path(), "w") as f:
            auth.write(f)

        self.verify_authentication()

    def _authenticate_with_profile(
        self,
        profile_name: str,
        region_name: str
    ) -> None:
        """ Authenticate with local profile stored in ~/.aws/config.

        Args:
            profile_name: profile name stored in ~/.aws/config.
                          Must begin with 'profile'.
                          E.g. [profile myprofilename]
            region_name: region name, e.g. eu-west-1

        """

        logger.debug("Authenticating with profile")
        session = boto3.Session(region_name=region_name,
                                profile_name=profile_name)
        self._client = session.client('s3')

    def _authenticate_with_access_key(
        self,
        aws_access_key_id: str,
        aws_secret_access_key: str,
        region_name: str
    ) -> None:
        """ Authenticate with credentials.

        Args:
            aws_access_key_id: access key id
            aws_secret_access_key: secret access key
            region_name: region name, e.g. eu-west-1

        """

        logger.debug("Authenticate with access key")
        if not aws_access_key_id or not aws_secret_access_key:
            raise AWSS3NoNoCredentialsProvidedError(
                aws_access_key_id_name=RSC.LDV_AWS_ACCESS_KEY_ID,
                aws_secret_access_key_name=RSC.LDV_AWS_SECRET_ACCESS_KEY)

        session = boto3.Session(region_name=region_name,
                                aws_access_key_id=aws_access_key_id,
                                aws_secret_access_key=aws_secret_access_key)
        self._client = session.client('s3')

    @staticmethod
    def get_auth_values() -> AwsAuthDto:
        """ Return the auth values from .ldv/auth.

        Returns:
            authentication values in AwsAuthDto object.

        """

        if not os.path.exists(BaseAuth.get_auth_path()):
            raise FileNotFoundError(
                "Auth file not found. "
                "Must run 'ldv auth' first."
            )

        try:
            auth = configparser.ConfigParser()
            auth.read(BaseAuth.get_auth_path())
        except Exception as e:
            logger.error("Error when reading auth")
            raise AuthReadError().with_traceback(e.__traceback__)

        # Try to find correct enum from string
        try:
            # Must use .upper() to match with enum name
            # when parsing string to enum
            auth_type = AwsAuthType[
                auth[AAC.AWS_AUTH][AAC.TYPE].upper()
            ]
        except Exception as e:
            logger.warning(f"Auth type in auth file is incorrect. "
                           f"Using 'none' instead. '{repr(e)}'")
            auth_type = AwsAuthType.NONE

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

        return AwsAuthDto(
            provider=provider,
            auth_type=auth_type,
            region_name=auth[AAC.AWS_AUTH][AAC.REGION_NAME],
            profile_name=auth[AAC.AWS_AUTH][AAC.PROFILE_NAME]
        )

    def verify_authentication(self) -> None:
        """ Verify that auth values exist and have correct values.

        Also do validation that credentials work"""

        auth_values: AwsAuthDto = self.get_auth_values()
        if auth_values.auth_type == AwsAuthType.NONE:
            raise InvalidAuthenticationTypeError(AwsAuthType.valid_values())

        # Verify profile
        if auth_values.auth_type == AwsAuthType.PROFILE:
            # Check if profile_name is in ~/.aws/config
            aws_config = AwsConfig()
            contains_profile: bool = aws_config.contains_profile(
                auth_values.profile_name)
            if not contains_profile:
                raise NoAuthenticationProfileFoundError(
                    auth_values.profile_name
                )

        # Verify credentials
        if auth_values.auth_type == AwsAuthType.ENV_CREDENTIALS:
            # Check if env variables are set
            access_key_id = os.environ.get(
                RSC.LDV_AWS_ACCESS_KEY_ID)
            secret_access_key = os.environ.get(
                RSC.LDV_AWS_SECRET_ACCESS_KEY)
            if not access_key_id or not secret_access_key:
                raise NoAuthenticationEnvironmentVariablesSetError()
