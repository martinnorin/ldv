"""Module for url validation. """


from typing import List
from ldv.constants.remote import UrlSchemeConstants
from ldv.utils.constants_helper import ConstantsHelper
from ldv.utils.exceptions import UnsupportedRemoteStorageSchemeError
from ldv.utils.url_helper import UrlHelper


class UrlValidation:
    """Class for url validation. """

    @staticmethod
    def validate(url: str) -> bool:
        """Validate url.

        Validate url that it is in correct format:
        <scheme>://<bucket>/<optional path>

        Example:
        s3://mybucket/folder1

        Args:
            url: url to validate

        Returns:
            True if url is in valid format. False otherwise.

        Raises:
            ValueError if invalid format
            UnsupportedRemoteStorageSchemeError: if url starts
                with invalid schema.

        """

        # Validate format
        UrlHelper.is_valid(url=url)

        # Get url scheme
        scheme = UrlHelper.get_scheme(url=url, validate_url=False)

        # Get valid schemes
        valid_schemes: List[str] = ConstantsHelper.get_constants_values(
            UrlSchemeConstants
        )

        # Make valid schemes lowercase
        valid_schemes = [sch.lower() for sch in valid_schemes]

        # Check if scheme is valid
        if scheme.lower() not in valid_schemes:
            raise UnsupportedRemoteStorageSchemeError(
                url_scheme=scheme,
                supported_url_schemes=valid_schemes)

        return True
