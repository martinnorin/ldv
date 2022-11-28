""" Module for auth dataclasses. """

from dataclasses import dataclass

from ldv.enums.auth import AwsAuthType


@dataclass
class AuthDto:
    """ Dataclass for authentication. """

    auth_type: AwsAuthType
    region_name: str
    profile_name: str

@dataclass
class BaseAuthProviderDto:
    """ Dataclass for base authentication."""

    name: str

@dataclass
class BaseAuthDto:
    """ Dataclass for base authentication."""

    provider: BaseAuthProviderDto

@dataclass
class AwsAuthDto(BaseAuthDto):
    """ Dataclass for AWS authentication. """

    auth_type: AwsAuthType
    region_name: str
    profile_name: str
