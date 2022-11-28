""" Module for custom exceptions. """

from typing import List


class FileNotUnderFolderError(Exception):
    """ Error class when file is not under folder. """

    def __init__(self, filepath, rootpath) -> None:
        """ Init.

        Args:
            filepath: filepath that must be under rootpath
            rootpath: root path

        """
        message = (
            f"File {filepath} not found on under path {rootpath}. "
            f"Only files under {rootpath} can be version tracked."
        )
        super().__init__(message)


class FileNotFoundOnRemoteError(Exception):
    """ Error class when file is not found on remote storage. """

    def __init__(self, filepath) -> None:
        """ Init.

        Args:
            filepath: filepath that is not found on remote storage

        """
        super().__init__(f"{filepath} not found on remote storage")


class ConfigMissingKeyError(Exception):
    """ Error class when config is missing key. """

    def __init__(self, section, missing_key) -> None:
        """ Init.

        Args:
            section: section in config file
            missing_key: missing key under section

        """
        super().__init__(f"Config is missing key '{missing_key}' "
                         f"under section {section}")


class ConfigMissingSectionError(Exception):
    """ Error class when config file is missing sections. """

    def __init__(self, missing_section) -> None:
        """ Init.

        Args:
            missing_section: missing section in config file

        """

        super().__init__(f"Config is missing section '{missing_section}'")


class ConfigReadError(Exception):
    """ Error class when error occurs when reading .ldv/config file. """

    def __init__(self) -> None:
        """ Init. """

        super().__init__("Error when reading config file")


class AuthReadError(Exception):
    """ Error class when there is an error reading .ldv/auth file. """

    def __init__(self) -> None:
        """ Init. """

        super().__init__("Error when reading auth file")


class AuthenticationVerificationError(Exception):
    """ Error class when verifying authenctication fails. """

    def __init__(self) -> None:
        """ Init. """

        super().__init__(
            "Error verifying auth. Must run 'ldv init' first."
        )


class InvalidAuthenticationTypeError(Exception):
    """ Error class when authentication file has invalid auth type. """

    def __init__(self, valid_auth_types: List[str]) -> None:
        """ Init.

        Args:
            valid_auth_types: list of valid auth types

        """
        valid_auth_types = [f"'{at}'" for at in valid_auth_types]
        super().__init__(
            f"Invalid auth type provided. "
            f"Valid auth types are {', '.join(valid_auth_types)}")


class NoAuthenticationProfileFoundError(Exception):
    """ Error class for no authentication profile found.

    Used for when profile in auth file
    doesn't exist in ~/.aws/config.
    """

    def __init__(self, profile_name) -> None:
        """ Init.

        Args:
            profile_name: missing profile name

        """
        super().__init__(
            f"Profile '{profile_name}' "
            "not found in ~/.aws/config"
        )


class NoAuthenticationEnvironmentVariablesSetError(Exception):
    """ Error class not set env var.

    Used when environmental variables
    not set for authentication
    """

    def __init__(self) -> None:
        """ Init. """

        super().__init__(
            "Authentication failed. "
            "Environment variables not set."
        )


class NotAuthenticatedError(Exception):
    """ Error class when authentication has not been performed. """

    def __init__(self) -> None:
        """ Init. """

        super().__init__(
            "Cannot initialize client, not authenticated. "
            "Must run 'ldv auth' first"
        )


class AWSS3NoNoCredentialsProvidedError(Exception):
    """ Error class when no AWS S3 credentials have been provided. """

    def __init__(
        self,
        aws_access_key_id_name,
        aws_secret_access_key_name
    ) -> None:
        """ Init.

        Args:
            aws_access_key_id_name: missing env var
            aws_secret_access_key_name: missing env var

        """

        super().__init__(
            "No credentials provided for AWS S3 authentication. "
            "Must provide values in environmental variables "
            f"{aws_access_key_id_name} and "
            f"{aws_secret_access_key_name}"
        )


class AWSS3AuthenticationValidationError(Exception):
    """ Error class when validating AWS S3 credentials. """

    def __init__(self) -> None:
        """ Init. """

        super().__init__(
            "Error when validating AWS credentials. "
            "Must provide profile or environmental variables "
            "for authentication. Also you must have access to "
            "AWS S3 for profile or environmental variable credentials"
        )


class VersionError(Exception):
    """ Error class when version is missing.

    Used when version is not provided or
    not found in .digest file
    """

    def __init__(self) -> None:
        """ Init. """

        super().__init__(
            "No version provided or found in .digest file."
        )


class NotRelativeFilepathError(Exception):
    """ Error class when filepath is not relative. """

    def __init__(self, filepath) -> None:
        """ Init.

        Args:
            filepath: filepath that must be relative

        """

        super().__init__(
            f"'{filepath}' must be relative filepath"
        )


class ConfigPathNotFoundError(Exception):
    """ Error class when path in .ldv/config path doesn't exist. """

    def __init__(self, path) -> None:
        """ Init.

        Args:
            path: path that doesn't exist

        """

        super().__init__(
            f"Path '{path}' specified in .ldv/config doesn't exist."
        )


class UnsupportedRemoteStorageSchemeError(Exception):
    """ Error class when remote storage scheme is not supported. """

    def __init__(
        self,
        url_scheme: str,
        supported_url_schemes: List[str]
    ) -> None:
        """ Init.

        Args:
            url_scheme: provided url scheme
            supported_schemes: supported url schemes

        """

        super().__init__(
            f"Remote storage scheme '{url_scheme}' is not supported. "
            f"Supported schemes are {supported_url_schemes}, case insensitive."
        )
