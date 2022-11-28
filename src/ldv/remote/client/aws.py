
import logging
import os
import boto3
from botocore.exceptions import ClientError

from ldv.dto.auth import AwsAuthDto
from ldv.enums.auth import AwsAuthType
from ldv.remote.auth.base import BaseAuth
from ldv.remote.client.base import BaseClient
from ldv.utils.exceptions import (
    AWSS3AuthenticationValidationError,
    AWSS3NoNoCredentialsProvidedError,
    NotAuthenticatedError
)
from ldv.constants.remote import RemoteStorageConstants as RSC

# Create separate logger with file as name
logger = logging.getLogger(__name__)

class AwsClient(BaseClient):

    def __init__(self, auth: BaseAuth) -> None:
        auth_values: AwsAuthDto = auth.get_auth_values()
        # Sets self.client
        self._init_client(auth_values)

    def _init_client(self, auth_values: AwsAuthDto) -> None:
        """ Initalize client based on auth type.

        Performs authentication using local profile
        or credentials in environmental variables based
        on authentication type.

        Args:
            auth_values: authentication info
        """

        # Validate authenticate type
        if auth_values.auth_type == AwsAuthType.NONE:
            raise NotAuthenticatedError()

        if auth_values.auth_type == AwsAuthType.PROFILE:
            # Authenticate with local profile
            self._authenticate_with_profile(
                profile_name=auth_values.profile_name,
                region_name=auth_values.region_name)
        elif auth_values.auth_type == AwsAuthType.ENV_CREDENTIALS:
            # Get credentials from environment variables
            aws_access_key_id = os.environ.get(
                RSC.LDV_AWS_ACCESS_KEY_ID,
                ""
            )
            aws_secret_access_key = os.environ.get(
                RSC.LDV_AWS_SECRET_ACCESS_KEY,
                ""
            )
            self._authenticate_with_access_key(
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                region_name=auth_values.region_name
            )

        self.validate_credentials()

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
        self.client = session.client('s3')

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
        self.client = session.client('s3')

    def validate_credentials(self) -> None:
        """ Validate AWS credentials by trying to list buckets in S3. """

        try:
            self.client.list_buckets()
        except ClientError as ce:
            raise AWSS3AuthenticationValidationError().with_traceback(
                ce.__traceback__)

        logger.debug("Successful validation with AWS credentials")