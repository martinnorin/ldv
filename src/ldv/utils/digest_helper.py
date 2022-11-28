""" Module for digest things. """

import os
import json
from json.decoder import JSONDecodeError
import hashlib
from datetime import datetime
from dateutil import parser

from ldv.utils.config import Config, ConfigDto
from ldv.constants.versioning import (
    VersioningConstants as VC,
    DigestConstants as DC
)
from ldv.utils.exceptions import NotRelativeFilepathError
from ldv.dto.digest import DigestDto


class DigestHelper:
    """ Class for digest methods. """

    @staticmethod
    def build_digest_filename(filename: str) -> str:
        """ Adds digest file ending to file.

        Args:
            filename: filename to build digest from. E.g. myfile.py

        Returns:
            filename of digest. E.g. myfile.py.digest

        """

        return f"{filename}.{VC.DIGEST_FILE_ENDING}"

    @staticmethod
    def get_existing_digest(relative_filename: str) -> DigestDto:
        """ Reads digest file of filename.

        Args:
            relative_filename: relative name of file. E.g. myfile.py

        Raises:
            FileNotFoundError if digest file not found

        Returns:
            Digest object if the file exists

        """

        existing_digest: dict = {}
        digest_file_name = DigestHelper.build_digest_filename(
            relative_filename
        )
        if not os.path.exists(digest_file_name):
            raise FileNotFoundError(
                f"No digest file found for {relative_filename}'. "
                "You must version track the file first."
            )

        with open(digest_file_name, "r") as fr:
            try:
                existing_digest = json.load(fr)
            except JSONDecodeError:
                # Swallow error if file is empty
                pass
        # Convert timestamp from str to datetime
        existing_digest[DC.TIMESTAMP] = parser.parse(
            existing_digest[DC.TIMESTAMP]
        )

        # Handle new key that might be missing in old digest files
        if DC.REMOTE_FILEPATH not in existing_digest:
            existing_digest[DC.REMOTE_FILEPATH] = ""

        return DigestDto(**existing_digest)

    @staticmethod
    def remove_digest_ending(filename: str) -> str:
        """ Removes digest file ending from file.

        Args:
            filename: filename to remove digest from. E.g. myfile.py.digest

        Returns:
            content filename. E.g. myfile.py

        """

        return filename.replace(
            f".{VC.DIGEST_FILE_ENDING}",
            "")

    @staticmethod
    def build_file_digest(filepath: str) -> DigestDto:
        """ Build digest object of file.

        Args:
            filepath: path to file. Must be relative

        Raises:
            NotRelativeFilepathError if filepath is absolute

        Returns:
            digest dict

        """

        if os.path.isabs(filepath):
            raise NotRelativeFilepathError(filepath)

        file_stat = os.stat(filepath)

        # Read content of file in bytes
        with open(filepath, "rb") as f:
            content: bytes = f.read()

        hexdigest = DigestHelper._hash_content(
            content=content
        )

        remote_filepath: str = DigestHelper._build_remote_filepath(filepath)

        digest: DigestDto = DigestDto(
            timestamp=datetime.utcnow(),
            hexdigest=hexdigest,
            size=file_stat.st_size,
            filepath=filepath,
            remote_filepath=remote_filepath
        )

        return digest

    @staticmethod
    def _build_remote_filepath(filepath: str) -> str:
        """ Build remote filepath.

        Based on remote url in .ldv/config file and local filepath,
        build remote filepath

        Args:
            filepath: local filepath

        Returns:
            full remote filepath of a file

        """

        config: ConfigDto = Config().get_config_values()
        return os.path.join(config.remote.url, filepath)

    @staticmethod
    def _hash_content(content: bytes) -> str:
        """ Hash content of bytes.

        Hashing is done using md5

        Args:
            content: data in bytes to hash

        Returns:
            string of hashed content, hexdigest

        """

        return hashlib.md5(content).hexdigest()

    @staticmethod
    def save_digest_file(filename: str) -> DigestDto:
        """ Save digest file.

        Builds the digest from the content file
        and saves the digest file with same name as file
        with an additional file ending. The file is saved in
        json format

        Args:
            filename: relative filepath of file

        Returns:
            digest object

        """

        digest: DigestDto = DigestHelper.build_file_digest(filename)
        digest_file_name: str = DigestHelper.build_digest_filename(filename)
        with open(digest_file_name, "w") as fw:
            # Use indent=4 to make the resulting file easier to read
            json.dump(obj=digest.to_dict(), fp=fw, indent=4)

        return digest
