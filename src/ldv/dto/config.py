""" Module for config dataclasses. """

from dataclasses import dataclass


@dataclass
class ConfigRemoteDto:
    """ Remote config data class.

    Data class for values under remote
    section in config file
    """

    url: str
    upload: bool


@dataclass
class ConfigLocalDto:
    """ Local config data class.

    Data class for values under local
    section in config file
    """

    path: str


@dataclass
class ConfigDto:
    """ Config data class.

    Container class for values in remote and local
    sections in config file
    """

    remote: ConfigRemoteDto
    local: ConfigLocalDto
