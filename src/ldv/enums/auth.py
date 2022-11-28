""" Module for auth enums. """

from typing import List
from enum import Enum

class AwsAuthType(Enum):
    """ Enum class for authentication type. """

    NONE = "none"
    PROFILE = "profile"
    ENV_CREDENTIALS = "env_credentials"

    @classmethod
    def available_values(cls) -> List[str]:
        """ Get the available values.

        Returns:
            list of all enum values

        """

        return [e.value for e in cls]

    @classmethod
    def valid_values(cls) -> List[str]:
        """ Get the valid values.

        All values except none are valid

        Returns:
            list of all valid enum values

        """

        return [e.value for e in cls if e != AwsAuthType.NONE]

class LdvRemoteProvider(Enum):

    NONE = "none"
    AWS = "AWS"