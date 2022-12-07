import logging
import os
from pathlib import Path
from typing import Optional

from ldv.constants.versioning import VersioningConstants as VC
from ldv.dto.config import ConfigDto
from ldv.dto.digest import DigestDto
from ldv.enums.remote import RemoteStorageFileType
from ldv.remote.auth.base import BaseAuth
from ldv.utils.cache_helper import CacheHelper
from ldv.utils.config import Config
from ldv.remote.base import BaseRemote
from ldv.utils.digest_helper import DigestHelper
from ldv.utils.exceptions import FileNotFoundOnRemoteError, FileNotUnderFolderError, VersionError

# Create separate logger with file as name
logger = logging.getLogger(__name__)

class Versioning:

    _CURRENT_VERSION = " (CURRENT VERSION)"
    _OLDER_VERSION = " (OLDER VERSION)"

    def __init__(self) -> None:
        # Init from config
        self._config: Config = Config()
        self._config_values: ConfigDto = self._config.get_config_values()
        self._auth_values = BaseAuth.get_base_auth_values()
        self._init_from_config(self._config_values)

    def _init_from_config(self, config: ConfigDto):
        """ Initialize instance from config values.

        Args:
            config: config values

        """

        self._config.verify_config_values_from_object(config)
        self._remote: BaseRemote = BaseRemote.get_remote(
            url=config.remote.url,
            provider=self._auth_values.provider
        )
        self._upload: bool = config.remote.upload
        self._set_paths(path=config.local.path)

    def _set_paths(self, path: str) -> None:
        """ Set paths.

        Used for uploading, downloading, and copying files.

        self._parent_path is full path of parent folder of path.
          Used for creating relative path of file if abs path is provided.
          Absolute: Yes
          Example: /Users/myusername/path/to/data
        self._remote_base_path is found in url to remote storage
          Used for building correct remote file path for upload and download.
          It doesn't need to be provided.
          Absolute: No
          Example: ldv_test in s3://niva-nlu-dev/ldv_test/
                                     temp_data/test_absolute_versioning.py
        """

        if not os.path.isabs(path):
            path = os.path.abspath(path)

        self._parent_path = str(Path(path).parent)
        self._remote_base_path = self._remote.remote_base_path

    def _to_relative_path(self, filepath: str) -> str:
        """ Convert to relative path.

        Removes parent path from filepath if it is absolute path.
        Otherwise, returns filepath as is.

        Args:
            filepath: filepath to convert to relative path

        Returns:
            relative filepath

        """

        if os.path.isabs(filepath):
            filepath = filepath.replace(self._parent_path + "/", "")

        return filepath

    def _upload_file(self, local_relative_filepath: str, version: str) -> None:
        """ Upload file.

        Args:
            local_relative_filepath: Relative path to file
            version: file version

        """

        logger.debug(f"Started uploading '{local_relative_filepath}' "
                     f"with version '{version}'")
        # Build remote digest file based on filepath and version
        digest_remote_path = \
            Versioning._get_remote_digest_path(
                base_remote_path=self._remote_base_path,
                relative_remote_path=local_relative_filepath,
                version=version)
        # Build remote content file based on filepath and version
        content_remote_path = Versioning._get_remote_content_path(
            base_remote_path=self._remote_base_path,
            relative_remote_path=local_relative_filepath,
            version=version)

        # CONTENT
        # Only upload if file doesn't already exist on remote
        if not self._remote.file_exists_on_remote(
                remote_filepath=content_remote_path):
            logger.debug("Uploading content")
            self._remote.upload_file(
                from_local_path=local_relative_filepath,
                to_remote_path=content_remote_path)
        else:
            logger.debug("Content already uploaded")

        digest_local_path = DigestHelper.build_digest_filename(
            local_relative_filepath)

        # DIGEST
        # Only upload if file doesn't already exist on remote
        if not self._remote.file_exists_on_remote(
                remote_filepath=digest_remote_path):
            logger.debug("Uploading digest")
            self._remote.upload_file(
                from_local_path=digest_local_path,
                to_remote_path=digest_remote_path)
        else:
            logger.debug("Digest already uploaded")
        logger.debug(f"File '{local_relative_filepath}' uploaded")

    @staticmethod
    def _get_remote_digest_path(
        base_remote_path: str,
        relative_remote_path: str,
        version: str
    ) -> str:
        """ Build remote digest path from values.

        Args:
            base_remote_path: remote base path from url
            relative_remote_path: same as path specified in .ldv/config
            version: version of file

        Returns:
            string with example format:
                "ldv_data_test/
                test_absolute_versioning.py/
                7860b1b81ad11b97e3785fb4571a355a/
                digest"

        """

        return Versioning._get_remote_full_path(
            base_remote_path,
            relative_remote_path,
            version,
            RemoteStorageFileType.DIGEST)

    @staticmethod
    def _get_remote_file_path(
        base_remote_path: str,
        relative_remote_path: str,
    ) -> str:
        """ Build remote file path from values.

        Args:
            base_remote_path: remote base path from url
            relative_remote_path: same as path specified in .ldv/config

        Returns:
            string with example format:
                "ldv_data_test/
                test_absolute_versioning.py"

        """

        base_remote_path_prefix: str = ""
        if base_remote_path:
            base_remote_path_prefix = base_remote_path + "/"
        return (f"{base_remote_path_prefix}"
                f"{relative_remote_path}")

    @staticmethod
    def _get_remote_full_path(
        base_remote_path: str,
        relative_remote_path: str,
        version: str,
        filetype: RemoteStorageFileType
    ) -> str:
        """ Build remote full path from values.

        Args:
            base_remote_path: remote base path from url
            relative_remote_path: same as path specified in .ldv/config
            version: version of file
            filetype: 'content' or 'digest'

        Returns:
            string with example format:
                "ldv_data_test/
                test_absolute_versioning.py/
                7860b1b81ad11b97e3785fb4571a355a/
                content"

        """
        base_remote_path_prefix: str = ""
        if base_remote_path:
            base_remote_path_prefix = base_remote_path + "/"

        return (f"{base_remote_path_prefix}"
                f"{relative_remote_path}/"
                f"{version}/"
                f"{filetype.value}")

    @staticmethod
    def _get_remote_content_path(
        base_remote_path: str,
        relative_remote_path: str,
        version: str
    ) -> str:
        """ Build remote content path from values.

        Args:
            base_remote_path: remote base path from url
            relative_remote_path: same as path specified in .ldv/config
            version: version of file

        Returns:
            string with example format:
                "ldv_data_test/
                test_absolute_versioning.py/
                7860b1b81ad11b97e3785fb4571a355a/
                content"

        """

        return Versioning._get_remote_full_path(
            base_remote_path,
            relative_remote_path,
            version,
            RemoteStorageFileType.CONTENT)

    def _store_file_in_local_cache(self, relative_filepath: str):
        """ Store a copy of the file in local cache.

        NOTE: In which scenario will we use the cached file?

        Args:
            relative_filepath: relative local filepath

        """

        CacheHelper.cache_file(relative_filepath)

    def _add_file_to_ignore(self, relative_filepath: str) -> None:
        """ Add file to ignore in .gitignore.

        The file to ignore is added to .gitignore on same level
        as the file. If the filename is already present, do nothing.

        Args:
            relative_filepath: relative path of file to ignore under
                               path specified in .ldv/config

        """

        # Folder name containing file to ignore
        relative_folder_path = os.path.dirname(relative_filepath)

        # Just filename without path
        filename = os.path.basename(relative_filepath)

        # Relative filepath of .gitignore file
        relative_gitignore_filepath = os.path.join(
            relative_folder_path,
            VC.GIT_IGNORE_FILE
        )

        # Check if filename already in .gitignore file
        filename_exists_in_gitignore = Versioning._content_in_file(
            filename,
            relative_gitignore_filepath
        )

        # Only add it if filename doesn't already exist
        if not filename_exists_in_gitignore:
            with open(relative_gitignore_filepath, "a") as f_append:
                f_append.write(f"{filename}\n")

    @staticmethod
    def _content_in_file(content: str, filepath: str) -> bool:
        """ Check if content is in file.

        Args:
            content: string to check existance in file
            filepath: file to open and check for content
        Returns:
            True if content exactly matches line in file.
            Else False.

        """

        if not os.path.exists(filepath):
            return False

        with open(filepath, "r") as f:
            for line in f.readlines():
                line = line.strip()
                if line == content:
                    return True

        return False

    def build_content_filename_by_version(
        self,
        filename: str,
        version: str
    ) -> str:
        """ Add the version to the end of the filename.

        Args:
            filename: filename. E.g. myfile.py
            version: version. E.g. 7860b1b81ad11b97adddf3a72e183a85

        Returns:
            filename and version as suffix.
            E.g. myfile.py.7860b1b81ad11b97adddf3a72e183a85

        """

        return f"{filename}.{version}"

    def track(self, filepath: str, upload: Optional[bool] = None) -> DigestDto:
        """ Version track file.

        Args:
            filepath: filepath, absolute or relative.
                      If relative, must start with path
                      that was used in 'init' command.
            upload: optional flag that overrides instance upload flag.
                    File will be uploaded if this is True.
                    If this is False, instance variable '_upload' is ignored.
                    If this is None, instance variable '_upload' is used.
                    If file not uploaded, it will be stored in local cache.

        Returns:
            Digest object
        """

        # Verify to catch error errors early
        self._config.verify_config_values_from_object(self._config_values)
        self._remote.verify_authentication()

        # Check if file exists
        # Except setting parent path,
        # this is only use of absolute path.
        abs_filepath = os.path.abspath(filepath)
        if not os.path.exists(abs_filepath):
            raise FileNotFoundError(f"File not found on path {abs_filepath}")

        # Check if file is under path in .ldv/config
        abspath_config_path = os.path.abspath(self._config_values.local.path)
        if not abs_filepath.startswith(abspath_config_path):
            raise FileNotUnderFolderError(abs_filepath, abspath_config_path)

        # Convert to relative path
        # NOTE: All the code is assuming the path is relative!
        relative_filepath = self._to_relative_path(filepath)

        logger.info(f"Version tracking '{relative_filepath}'")

        current_digest: DigestDto = DigestHelper.save_digest_file(
            relative_filepath
        )

        # TODO: store current version and timestamp in list inside file
        # locally and remote if should be uploaded

        # If method parameter is provided,
        # use that one.
        # Method parameter takes precedence over instance variable
        if upload is not None:
            if upload:
                logger.debug("Local upload variable is used")
                self._upload_file(local_relative_filepath=relative_filepath,
                                  version=current_digest.hexdigest)
        # Else, if instance variable is set, use it.
        elif self._upload:
            logger.debug("Instance upload variable is used")
            self._upload_file(local_relative_filepath=relative_filepath,
                              version=current_digest.hexdigest)

        # TODO: always cache file locally
        if not upload or not self._upload:
            self._store_file_in_local_cache(relative_filepath)

        self._add_file_to_ignore(relative_filepath=relative_filepath)

        return current_digest

    def track_all(self, upload: Optional[bool] = None) -> None:
        """ Version track all files under path specified in .ldv/config.

        # TODO: add subpath under path to version track

        Args:
            upload: flag to indicate if files should be uploaded
                    when version tracking them.

        """

        # Verify to catch error errors early
        self._config.verify_config_values_from_object(self._config_values)
        self._remote.verify_authentication()

        # Recursively find all files and folders under path
        for root, _, files in os.walk(self._config_values.local.path):
            for file in files:
                if (
                    file.endswith(VC.DIGEST_FILE_ENDING) or
                    file == VC.GIT_IGNORE_FILE
                ):
                    continue

                filepath = os.path.join(root, file)
                self.track(filepath=filepath, upload=upload)

    def download(
        self,
        digest_filepath: str,
        version: str = None,
        verify: bool = True
    ) -> None:
        """ Downloads tracked file that have .digest file locally.


        TODO: filepath should point to the .digest file
        TODO: refactor to reflect this

        If file with that name already exists locally,
        the local file will be renamed with current
        version as suffix. Then the remote file
        will be downloaded with the version tracked name.
        If the file exists and version is not provided, it will overwrite the
        file but a copy of the old file will be created with the version as
        suffix.

        Args:
            digest_filepath: filepath, absolute or relative.
                      If relative, must start with path
                      that was used in 'init' command.
                      Also, it must have .digest ending.
            version: is provided if want to download other version of file.
                     Version is same as hexdigest in .digest file.

        """

        if verify:
            # Verify to catch error errors early
            self._config.verify_config_values_from_object(self._config_values)
            self._remote.verify_authentication()

        # Convert from absolute path to relative path.
        # NOTE: All the code is assuming the path is relative!
        relative_digest_filepath: str = self._to_relative_path(digest_filepath)
        relative_filepath: str = DigestHelper.remove_digest_ending(
            relative_digest_filepath
        )

        logger.info(f"Downloading file '{relative_filepath}'")

        # Load digest file
        digest: DigestDto = DigestHelper.get_existing_digest(
            relative_filepath
        )

        version_to_use: str = ""
        if not version:
            version_info = Versioning._CURRENT_VERSION
            version_to_use = digest.hexdigest
        else:
            version_info = Versioning._OLDER_VERSION
            version_to_use = version

        if not version_to_use:
            raise VersionError()

        # TODO: check if file exists locally with same digest.

        logger.debug(f"Started downloading '{relative_filepath}' "
                     f"with version '{version_to_use}{version_info}'")

        # content_remote_path is relative path to find file
        # in the remote storage bucket.
        # E.g. ldv_test/temp_data/
        #        test_absolute_versioning.py/
        #        7fbaa1f02cf33f8941b8fefe7644d996/content
        # Scheme (s3) and bucket name (niva-nlu-dev) is not
        # part of content_remote_path
        content_remote_path = Versioning._get_remote_content_path(
            base_remote_path=self._remote_base_path,
            relative_remote_path=relative_filepath,
            version=version_to_use)

         # TODO: check if remote filepath exists in digest file.
        # Check if that is same as the one returned below.
        # If different, return and print warning.
        # Add flag to force download of file from path below and
        # not from path stored in digest file.

        # Check if file with version exists on remote storage
        if not self._remote.file_exists_on_remote(
                remote_filepath=content_remote_path):
            raise FileNotFoundOnRemoteError(content_remote_path)

        # Calculate digest of file if it exists, for comparison with
        # value in digest file
        calculated_in_memory_digest: Optional[DigestDto] = None
        if os.path.exists(relative_filepath):
            calculated_in_memory_digest = DigestHelper.build_file_digest(
                relative_filepath)

        # Check if version is different from calculated in-memory version,
        # if so, rename current file (if exists)
        # with calculated version as suffix
        # This will handle case when
        #   * version is provided to function
        #   * using version from digest file but they are different,
        #     for example when old version of file exists locally
        #     and digest file is fetched from git
        # If calculated_in_memory_digest is None it means that
        # the file doesn't exists locally and no need to rename it.
        if calculated_in_memory_digest is not None \
                and version_to_use != calculated_in_memory_digest.hexdigest:
            # new_local_content_path is
            # e.g. path/myfile.py.7860b1b81ad11b97adddf3a72e183a85
            new_local_content_path = self.build_content_filename_by_version(
                relative_filepath,
                calculated_in_memory_digest.hexdigest)

            # Rename current local file to filename + version as suffix
            os.rename(relative_filepath,
                      new_local_content_path)

        self._remote.download_file(
            from_remote_path=content_remote_path,
            to_local_path=relative_filepath
        )

        # Download the digest file also since
        # that file can differ from what we have locally.
        # This will overwrite existing digest file

        # digest_remote_path is relative path to find file digest
        # in the remote storage bucket.
        # E.g. ldv_test/temp_data/
        #        test_absolute_versioning.py/
        #        7fbaa1f02cf33f8941b8fefe7644d996/digest
        # Scheme (s3) and bucket name (niva-nlu-dev) is not
        # part of digest_remote_path
        digest_remote_path = \
            Versioning._get_remote_digest_path(
                base_remote_path=self._remote_base_path,
                relative_remote_path=relative_filepath,
                version=version_to_use)

        self._remote.download_file(
            from_remote_path=digest_remote_path,
            to_local_path=relative_digest_filepath)

        self._add_file_to_ignore(relative_filepath)

    def download_all(self) -> None:
        """ Download all files with digest from remote in path.

        # TODO: add subpath under path to download
        """

        # Verify to catch error errors early
        self._config.verify_config_values_from_object(self._config_values)
        self._remote.verify_authentication()

        # Recursively find all files and folders under path
        for root, _, files in os.walk(self._config_values.local.path):
            for file in files:
                if not file.endswith(
                    VC.DIGEST_FILE_ENDING
                ):
                    continue

                filepath = os.path.join(root, file)
                self.download(filepath, verify=False)

    def get_versions(self, digest_filepath: str) -> dict:

        # Verify to catch error errors early
        self._config.verify_config_values_from_object(self._config_values)
        self._remote.verify_authentication()

        relative_digest_filepath: str = self._to_relative_path(digest_filepath)
        relative_filepath: str = DigestHelper.remove_digest_ending(
            relative_digest_filepath
        )

        remote_filepath = Versioning._get_remote_file_path(
            base_remote_path=self._remote_base_path,
            relative_remote_path=relative_filepath
        )

        versions: dict = self._remote.get_versions(
            remote_filepath=remote_filepath
        )
        versions["relative_filepath"] = relative_filepath
        return versions