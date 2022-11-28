import configparser
import logging
import os

from ldv.dto.config import ConfigDto, ConfigLocalDto, ConfigRemoteDto
from ldv.utils.exceptions import (
    ConfigReadError,
    ConfigMissingSectionError,
    ConfigMissingKeyError
)
from ldv.constants.config import ConfigConstants as CC
from ldv.utils.validation import UrlValidation

# Create separate logger with file as name
logger = logging.getLogger(__name__)


class Config:
    """ Config class for reading and writing files in .ldv/config. """

    def __init__(self) -> None:
        """ Create config file in .ldv folder if not already exists. """

        self._folder = ".ldv"
        self._filename = "config"
        self._config_path = os.path.join(self._folder, self._filename)

    @property
    def config_path(self) -> str:
        """ Returns the path to the config file. """

        return self._config_path

    def init(self, path: str, url: str, upload: bool) -> None:
        """ Initialize config with path, url, and upload flag.

        Validation of path and url is done before storing values.

        Args:
            path: path to folder containing files to version track.
                  Can be absolute or relative.
            url: url to remote storage
            upload: flag to indicate if files should be uploaded
                    when version tracking them.

        """

        if not os.path.exists(self._folder):
            os.mkdir(self._folder)

        # Remove trailing slash
        if url.endswith("/"):
            url = url[:-1]

        self.verify_config_values(path=path, url=url)

        logger.debug(f"Config.init, folder: '{self._folder}'")
        logger.debug(f"Config.init, abspath folder: "
                     f"'{os.path.abspath(self._folder)}'")
        config = configparser.ConfigParser()
        config[CC.REMOTE] = {
            CC.URL: url,
            CC.UPLOAD: str(upload)
        }
        config[CC.LOCAL] = {
            CC.PATH: path
        }

        with open(self._config_path, "w") as f:
            config.write(f)

        # Make sure that values have been written to file
        verify_config = configparser.ConfigParser()
        verify_config.read(self._config_path)
        # TODO: make sure that the actual values are
        # in the verify_config

    def get_config_values(self) -> ConfigDto:
        """ Get config values from .ldv/config.

        Returns:
            LdvConfig if everything goes well.

        Raises:
            FileNotFoundError
            ConfigReadError
            ConfigMissingSectionError
            ConfigMissingKeyError

        """

        if not os.path.exists(self._config_path):
            raise FileNotFoundError(
                f"Config file not found on path {self._config_path}.")

        try:
            config = configparser.ConfigParser()
            config.read(self._config_path)
        except Exception as e:
            raise ConfigReadError().with_traceback(e.__traceback__)

        # Check for missing sections
        if not config.has_section(CC.REMOTE):
            raise ConfigMissingSectionError(CC.REMOTE)

        if not config.has_section(CC.LOCAL):
            raise ConfigMissingSectionError(CC.LOCAL)

        # Check for missing keys
        if not config.has_option(CC.REMOTE, CC.URL):
            raise ConfigMissingKeyError(CC.REMOTE, CC.URL)

        if not config.has_option(CC.REMOTE, CC.UPLOAD):
            raise ConfigMissingKeyError(CC.REMOTE, CC.UPLOAD)

        if not config.has_option(CC.LOCAL, CC.PATH):
            raise ConfigMissingKeyError(CC.LOCAL, CC.PATH)

        ldv_config = ConfigDto(
            remote=ConfigRemoteDto(
                url=config[CC.REMOTE][CC.URL],
                upload=config[CC.REMOTE].getboolean(CC.UPLOAD)
            ),
            local=ConfigLocalDto(
                path=config[CC.LOCAL][CC.PATH]
            )
        )
        return ldv_config

    def verify_config_values(self, path: str, url: str):
        if not os.path.exists(path):
            raise FileNotFoundError(
                f"Unable to initialize. Path '{path}' not found."
            )

        UrlValidation().validate(url=url)

    def verify_config_values_from_object(self, config_values: ConfigDto):
        self.verify_config_values(
            config_values.local.path,
            config_values.remote.url
        )
