""" Url helper module. """


from typing import Tuple


class UrlHelper:
    """Url helper class. """

    @staticmethod
    def is_valid(url: str) -> bool:
        """Checks if url is valid.

        Args:
            url: url

        Returns:
            True if url is of format <scheme>://<path>.
            Otherwise, exception is raised.

        Raises:
            ValueError if url not contains '://'
            ValueError if url not contains scheme
            ValueError if url not contains path
            ValueError if url ends with "/"

        """
        # Try to split on '://'
        try:
            scheme, path = url.split("://")
        except ValueError:
            raise ValueError(f"Invalid url '{url}', must contain '://'")

        if not scheme:
            raise ValueError(f"Invalid url '{url}'. Scheme cannot be empty.")

        if not path:
            raise ValueError(f"Invalid url '{url}'. Path cannot be empty.")

        if path.endswith("/"):
            raise ValueError(
                f"Invalid url '{url}'. Path cannot end with '/'."
            )

        return True

    @staticmethod
    def get_scheme(url: str, validate_url: bool = True) -> str:
        """ Get url scheme.

        Args:
            url: url
            validate_url: if url should be validated.

        Returns:
            url schema. E.g. http, s3.

        Raises:
            ValueError if url is invalid

        """
        if validate_url:
            UrlHelper.is_valid(url)
        scheme, _ = UrlHelper._split_url(url=url)

        return scheme

    @staticmethod
    def get_path(url: str, validate_url: bool = True) -> str:
        """ Get path from url.

        Args:
            url: url
            validate_url: if url should be validated.
        Returns:
            string with path

        Raises:
            ValueError if url is invalid

        """
        if validate_url:
            UrlHelper.is_valid(url)
        _, path = UrlHelper._split_url(url=url)

        return path

    @staticmethod
    def _split_url(url: str) -> Tuple[str, str]:
        """Split url into scheme and path.

        Args:
            url: url to split

        Returns:
            tuple with (scheme, path)

        Raises:
            ValueError if split on '://' only returns one element,
            meaning that the url doesn't contain '://'

        """
        try:
            scheme, path = url.split("://")
        except ValueError:
            raise ValueError(f"Invalid url '{url}'. It must contain '://'")

        return scheme, path
