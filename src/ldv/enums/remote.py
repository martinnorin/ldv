""" Module for remote storage enums. """

from enum import Enum


class RemoteStorageFileType(Enum):
    """ Enum class for remote storage file type. """

    CONTENT = "content"
    DIGEST = "digest"
