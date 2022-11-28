import logging

from ldv.utils.config import Config

# Create separate logger with file as name
logger = logging.getLogger(__name__)

def init(path: str, url: str, upload: bool) -> None:
    """ Store info in config file.

    Args:
        path: can be absolute or relative path.
              Must exist or exception is thrown.
        url: url to remote storage
        upload: flag to indicate if files should be uploaded
                when version tracking them.
    """

    logger.info("Initializing")

    # Store config values in file
    Config().init(path=path, url=url, upload=upload)
