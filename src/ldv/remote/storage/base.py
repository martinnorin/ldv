""" Base class for remote storage. """

from typing import Literal, Union, overload

from ldv.remote.client.base import BaseClient

class BaseRemoteStorage:
    """ Base remote storage class.

    This class is never instantiated but inherited by
    specific remote storage types.
    """

    def __init__(self, url: str, client: BaseClient) -> None:
        self._client = client

    def upload_file(self, from_local_path: str, to_remote_path: str) -> None:
        """ Upload file from local path to remote path.

        Args:
            from_local_path: relative path of file to upload
            to_remote_path: remote storage path to upload file to.
                            Doesn't include bucket name.
                            E.g. if full url to file is
                            'https://niva-nlu-dev.s3-eu-west-1.amazonaws.com/
                            ldv_test/ldv_data_test/
                            test_versioning1.py/
                            17a5bc2b5ac8b1322b3b64cad38985db/content'.
                            Then to_remote_path is
                            'ldv_test/ldv_data_test/
                            test_versioning1.py/
                            17a5bc2b5ac8b1322b3b64cad38985db/content'

        """

        raise NotImplementedError()

    def download_file(self, from_remote_path: str, to_local_path: str) -> None:
        """ Download file from remote path to local path.

        Args:
            from_remote_path: remote storage path to download file from.
                              Doesn't include bucket name.
                              E.g. if full url to file is
                              'https://niva-nlu-dev.s3-eu-west-1.amazonaws.com/
                              ldv_test/ldv_data_test/
                              test_versioning1.py/
                              17a5bc2b5ac8b1322b3b64cad38985db/content'.
                              Then from_remote_path is
                              'ldv_test/ldv_data_test/
                              test_versioning1.py/
                              17a5bc2b5ac8b1322b3b64cad38985db/content'
            to_local_path: relative local path of file to download

        """

        raise NotImplementedError()

    # Overload function return type based on to_string flag
    @overload
    def load_file(
        self,
        from_remote_path: str,
        *,
        to_string: Literal[False] = False
    ) -> bytes:
        raise NotImplementedError()

    # Overload function return type based on to_string flag
    @overload
    def load_file(
        self,
        from_remote_path: str,
        *,
        to_string: Literal[True]
    ) -> str:
        raise NotImplementedError()

    def load_file(
        self,
        from_remote_path: str,
        *,
        to_string: bool = False
    ) -> Union[bytes, str]:
        """ Load file into memory from remote storage.

        Args:
            from_remote_path: remote storage path to load file from.
                              Doesn't include bucket name.
                              E.g. if full url to file is
                              'https://niva-nlu-dev.s3-eu-west-1.amazonaws.com/
                              ldv_test/ldv_data_test/
                              test_versioning1.py/
                              17a5bc2b5ac8b1322b3b64cad38985db/content'.
                              Then from_remote_path is
                              'ldv_test/ldv_data_test/
                              test_versioning1.py/
                              17a5bc2b5ac8b1322b3b64cad38985db/content'
            to_string: flag if content should be decoded to string from bytes
        Returns:
            bytes value of file content or
            string with file content values if to_string is True

        """

        raise NotImplementedError()

    def file_exists_on_remote(
        self,
        remote_filepath: str
    ) -> bool:
        """ Check if file exists on remote storage.

        Args:
            remote_filepath: remote filepath excluding bucket name
                             but including remote base path.
                             E.g. if full url to file is
                             'https://niva-nlu-dev.s3-eu-west-1.amazonaws.com/
                             ldv_test/ldv_data_test/
                             test_versioning1.py/
                             17a5bc2b5ac8b1322b3b64cad38985db/content'.
                             Then remote_filepath is
                             'ldv_test/ldv_data_test/
                             test_versioning1.py/
                             17a5bc2b5ac8b1322b3b64cad38985db/content'

        Returns:
            True if file exists on remote storage. False otherwise.

        """

        raise NotImplementedError()

    def get_versions(self, remote_filepath: str) -> None:
        raise NotImplementedError()

    @property
    def remote_base_path(self) -> str:
        """ Return the remote base path.

        The remote base path is the additional path in S3
        inside the bucket that is not part of the local path.
        The remote base path is extracted from the url found in .ldv/config.
        It is the part that follows after the initial bucket name, i.e.
        everything that is after the first slash (/) in the url.

        E.g. if full url to file is
                             'https://niva-nlu-dev.s3-eu-west-1.amazonaws.com/
                             ldv_test/ldv_data_test/
                             test_versioning1.py/
                             17a5bc2b5ac8b1322b3b64cad38985db/content'
                             and local path is 'ldv_data_test'
                             then the remote base path path is 'ldv_test'.

        """

        raise NotImplementedError()
