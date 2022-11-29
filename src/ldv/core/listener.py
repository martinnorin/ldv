""" Listen to file system events module. """

import time
import logging
from typing import Union
import time

from watchdog.events import (
    PatternMatchingEventHandler,
    DirCreatedEvent,
    DirModifiedEvent,
    DirDeletedEvent,
    FileCreatedEvent,
    FileModifiedEvent,
    FileDeletedEvent)
from watchdog.observers import Observer

from ldv.core.versioning import Versioning
from ldv.constants.versioning import VersioningConstants as VC

# Create separate logger with file as name
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class Listener(PatternMatchingEventHandler):
    """ Class for listening for file system events. """

    def __init__(self):
        """ Initalize class.

        Authenticates with profile or credentials (access key and secret).
        If profile is provided it will use that.
        Otherwise it will use aws_access_key_id and aws_secret_access_key.
        If neither are provided, the init will fail.

        Data will be versioned in S3 bucket on remote base path with path as
        subfolder to keep same structure locally and remote.
        """

        self._versioning = Versioning()

        # Watchdog
        patterns = "*"
        ignore_patterns = [f"*{VC.DIGEST_FILE_ENDING}"]
        ignore_directories = False
        case_sensitive = False
        super().__init__(patterns=patterns,
                         ignore_patterns=ignore_patterns,
                         ignore_directories=ignore_directories,
                         case_sensitive=case_sensitive)
        logger.debug("Listener successfully initialized")

        self._last_modified_file = None
        self._last_modified_time_ms = None

    # PatternMatchingEventHandler methods
    def on_created(
        self,
        event: Union[DirCreatedEvent, FileCreatedEvent]
    ) -> None:
        """ Called when a file or directory is created.

        Args:
            event: Event representing file/directory creation.

        """
        if event.is_directory:
            logger.debug(f"Created directory '{event.src_path}'")
        else:
            logger.debug(f"Created file '{event.src_path}'")
            self._versioning.track(filepath=event.src_path)

        return super().on_created(event)

    def on_modified(self, event: Union[DirModifiedEvent, FileModifiedEvent]):
        """ Called when a file or directory is modified.

        Args:
            event: Event representing file/directory modification.

        """
        if event.is_directory:
            logger.debug(f"Modifed directory '{event.src_path}'")
        else:
            logger.info(f"Modifed file '{event.src_path}'")

            modified_time = time.time() * 1000
            print(modified_time)
            time_threshold_ms = 100
            if event.src_path == self._last_modified_file:
                time_diff = modified_time - self._last_modified_time_ms
                print(modified_time)
                print(time_diff)
                if time_diff > time_threshold_ms:
                    self._last_modified_file = event.src_path
                    self._last_modified_time_ms = modified_time
                    logger.info("Version tracking 2")
                    self._versioning.track(filepath=event.src_path)
            else:
                logger.info("Version tracking 1")
                self._last_modified_file = event.src_path
                self._last_modified_time_ms = modified_time
                self._versioning.track(filepath=event.src_path)

        return super().on_modified(event)

    def on_deleted(
        self,
        event: Union[DirDeletedEvent, FileDeletedEvent]
    ) -> None:
        """ Called when a file or directory is deleted.

        Args:
            event: Event representing file/directory deletion.

        """

        if event.is_directory:
            logger.debug(f"Deleted directory '{event.src_path}'")
        else:
            logger.debug(f"Deleted file {event.src_path}")

        return super().on_deleted(event)
    # End PatternMatchingEventHandler methods

    def start_listening(self):
        """ Start listening for filesystem events.

        Start listening on path for files and folders
        that are created, modified, and deleted.

        Args:
            path: filesystem path to listen to recursively

        """
        logger.info("Start listening")

        go_recursively = True
        my_observer = Observer()
        my_observer.schedule(
            event_handler=self,
            path=self._versioning.path,
            recursive=go_recursively)

        my_observer.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            my_observer.stop()
            my_observer.join()
            logger.info("Stop listening")
