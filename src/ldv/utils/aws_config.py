""" Module for accessing ~/.aws/config. """

import os
import configparser


class AwsConfig:
    """ Class for accessing AWS config in ~/.aws/config. """

    def __init__(self) -> None:
        """ Reading ~/.aws/config file. """

        self._aws_config = configparser.ConfigParser()
        aws_config_path = os.path.expanduser("~/.aws/config")
        self._aws_config.read(aws_config_path)

    def contains_profile(self, profile: str) -> bool:
        """ Check if profile is a section in ~/.aws/config.

        Args:
            profile: profile name.

        """

        contains_profile: bool = self._aws_config.has_section(
            f"profile {profile}")
        return contains_profile
