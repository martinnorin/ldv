
import logging
from typing import List, Literal, Union, overload


from ldv.remote.client.aws import AwsClient
from ldv.remote.storage.base import BaseRemoteStorage
from ldv.utils.url_helper import UrlHelper
from ldv.enums.remote import RemoteStorageFileType

# Create separate logger with file as name
logger = logging.getLogger(__name__)

class AwsRemoteStorage(BaseRemoteStorage):
    """ AWS remote storage class. """

    def __init__(self, url: str, client: AwsClient) -> None:
        """ Init S3 remote storage.

        Args:
            url: url to remote storage

        """
        super().__init__(url=None, client=client.client)

        path = UrlHelper.get_path(url)

        # Split into bucket and remote base path
        # E.g. mybucket/mypath/subpath split into
        # ['mybucket', 'mypath/subpath']
        if "/" in path:
            bucket, remote_base_path = path.split("/", 1)
        else:
            bucket = path
            remote_base_path = None
        self._bucket = bucket
        self._remote_base_path = remote_base_path

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
        logger.debug(f"Uploading file from "
                     f"'{from_local_path}' to "
                     f"'{self._bucket} {to_remote_path}'")
        self._client.upload_file(from_local_path,
                                 self._bucket,
                                 to_remote_path)

    def download_file(self, from_remote_path, to_local_path) -> None:
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
        logger.debug(f"Downloading file from "
                     f"'{from_remote_path}' to '{to_local_path}'")

        self._client.download_file(self._bucket,
                                   from_remote_path,
                                   to_local_path)

    # Overload function return type based on to_string flag
    @overload
    def load_file(
        self,
        from_remote_path: str,
        *,
        to_string: Literal[False] = False
    ) -> bytes:
        pass  # Actual implementation in non-overloaded function load_file

    # Overload function return type based on to_string flag
    @overload
    def load_file(
        self,
        from_remote_path: str,
        *,
        to_string: Literal[True]
    ) -> str:
        pass  # Actual implementation in non-overloaded function load_file

    def load_file(
        self,
        from_remote_path: str,
        *,
        to_string: bool = False
    ) -> Union[bytes, str]:
        """ Load file into memory from S3.

        Args:
            from_remote_path: S3 path to load file from.
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

        response = self._client.get_object(
            Bucket=self._bucket,
            Key=from_remote_path
        )

        body: bytes = response["Body"].read()
        if to_string:
            return body.decode("utf-8")
        return body

    def file_exists_on_remote(self, remote_filepath) -> bool:
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
        response = self._client.list_objects_v2(
            Bucket=self._bucket,
            Prefix=remote_filepath,
        )
        for obj in response.get('Contents', []):
            if obj['Key'] == remote_filepath:
                return True
        return False

    def get_versions(self, remote_filepath: str) -> dict:
        response = self._client.list_objects_v2(
            Bucket=self._bucket,
            Prefix=remote_filepath,
        )
        versions: dict = {
            "remote_filepath": remote_filepath
        }
        versions_list: List[dict] = []
        for obj in response.get('Contents', []):
            version_dict: dict = {}
            filename: str = obj["Key"]
            if filename.endswith(RemoteStorageFileType.DIGEST.value):
                continue

            last_modified: str = obj["LastModified"]
            size: str = obj["Size"]
            version: str = filename\
                .replace(remote_filepath + "/", "")\
                .replace("/" + RemoteStorageFileType.CONTENT.value, "")

            version_dict["version"] = version
            version_dict["size"] = size
            version_dict["last_modified"] = last_modified
            versions_list.append(version_dict)
        versions["versions"] = versions_list
        return versions

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

        Returns:
            remote base path string.

        """

        return self._remote_base_path
