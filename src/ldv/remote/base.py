from typing import Any, Dict

from ldv.constants.remote import UrlSchemeConstants
from ldv.enums.auth import LdvRemoteProvider
from ldv.remote.auth.aws import AwsAuth
from ldv.remote.auth.base import BaseAuth
from ldv.remote.client.aws import AwsClient
from ldv.remote.client.base import BaseClient
from ldv.remote.storage.aws import AwsRemoteStorage
from ldv.remote.storage.base import BaseRemoteStorage
from ldv.utils.url_helper import UrlHelper


class BaseRemote:

    remote_storage_url_schemes: Dict[str, Any] = {
        UrlSchemeConstants.S3: AwsRemoteStorage
    }
    auth_providers: Dict[str, Any] = {
        LdvRemoteProvider.AWS: AwsAuth
    }
    client_providers: Dict[str, Any] = {
        LdvRemoteProvider.AWS: AwsClient
    }

    def __init__(
        self,
        auth: BaseAuth,
        client: BaseClient,
        storage: BaseRemoteStorage
    ) -> None:
        self._auth: BaseAuth = auth
        self._client: BaseClient = client
        self._storage: BaseRemoteStorage = storage


    def verify_authentication(self):
        self._auth.verify_authentication()
        self._client.validate_credentials()

    @property
    def remote_base_path(self) -> str:
        return self._storage.remote_base_path

    def file_exists_on_remote(self, remote_filepath) -> bool:
        return self._storage.file_exists_on_remote(
            remote_filepath=remote_filepath
        )

    def upload_file(self, from_local_path, to_remote_path):
        self._storage.upload_file(
            from_local_path=from_local_path,
            to_remote_path=to_remote_path
        )

    def download_file(self, from_remote_path: str, to_local_path: str) -> None:
        self._storage.download_file(
            from_remote_path=from_remote_path,
            to_local_path=to_local_path
        )

    def get_versions(self, remote_filepath: str) -> dict:
        versions: dict = self._storage.get_versions(
            remote_filepath=remote_filepath
        )
        return versions

    @staticmethod
    def get_remote(url: str, provider: LdvRemoteProvider) -> "BaseRemote":
        """ Get remote based on url.

        Args:
            url: url that must be in the format of
                <scheme>://<path>

        Returns:
            BaseRemote class based on scheme and provider

        """
        # Auth
        auth: BaseAuth = BaseRemote.auth_providers[
            provider
        ]()

        # Client
        client: BaseClient = BaseRemote.client_providers[
            provider
        ](auth=auth)

        # Storage
        url_scheme: str = UrlHelper.get_scheme(url=url)
        storage: BaseRemoteStorage = BaseRemote.remote_storage_url_schemes[
            url_scheme.lower()
        ](url=url, client=client)

        return BaseRemote(auth=auth, client=client, storage=storage)