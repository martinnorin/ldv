""" Module for handling cached files. """

import os
import shutil
from typing import Optional

from ldv.dto.digest import DigestDto
from ldv.utils.digest_helper import DigestHelper


class CacheHelper:
    """ Class for helping with cache. """

    CACHE_FOLDER = ".ldv_cache"

    @staticmethod
    def cache_file(filepath) -> None:
        """ Create a copy of the file in .ldv_cache.

        Args:
            filepath: filepath

        """

        # Create folders if not exist
        os.makedirs(
            os.path.join(
                CacheHelper.CACHE_FOLDER,
                os.path.dirname(filepath)
            ),
            exist_ok=True
        )

        # Copy file to cache folder
        shutil.copy(
            filepath,
            os.path.join(
                CacheHelper.CACHE_FOLDER,
                filepath
            )
        )

    @staticmethod
    def is_file_cached(relative_filepath: str) -> bool:
        """ Checks if file is stored in cache folder.

        Args:
            relative_filepath: relative filepath where file is normally stored

        Returns:
            True if file exists in cached folder. Otherwise, False

        """

        cached_filepath = os.path.join(
            CacheHelper.CACHE_FOLDER,
            relative_filepath
        )
        return os.path.exists(cached_filepath)

    @staticmethod
    def get_cached_file_digest(relative_filepath: str) -> Optional[DigestDto]:
        """ Get cached file digest.

        Args:
            relative_filepath: name of file. E.g. myfile.py

        Raises:
            FileNotFoundError if digest file not found

        Returns:
            dict of digest values if the file exists. Otherwise, None.

        """

        cached_filepath = os.path.join(
            CacheHelper.CACHE_FOLDER,
            relative_filepath
        )
        return DigestHelper.get_existing_digest(cached_filepath)

    @staticmethod
    def restore_cached_version(relative_filepath: str) -> None:
        """ Restore locally cached version of file.

        Args:
            relative_filepath: TODO:

        """

        # TODO: implement this
        raise NotImplementedError()
