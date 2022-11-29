from typing import Optional
import click

from ldv.core.listener import Listener
from ldv.core.versioning import Versioning

@click.group(name="listener")
def listener():
    """ Listening commands.

    Commands for listening to changes to folders and files
    under path specified in 'init' command.
    """
    pass  # pylint: disable=unnecessary-pass


@listener.command(name="start")
@click.option(
    "--scan",
    "-s",
    is_flag=True,
    default=False,
    help="Scan directories recursively for files "
         "to version track.")
@click.option(
    "--dont-upload",
    "-du",
    default=None,
    is_flag=True,
    help="Don't upload file to remote after version tracking")
def start(scan: bool, dont_upload: Optional[bool] = None):
    """ Start listening.

    Start listening for changes to folders and files
    under path specified in 'init' command.

    \b
    Args:
        scan: flag to indicate if a scan of all folders under
              path specified in the 'init' command should be
              performed before starting to listen to changes.
        dont_upload: optional flag used to not upload file when tracking it.

    """

    if scan:
        upload = None
        if dont_upload:
            upload = not dont_upload
        Versioning().track_all(upload=upload)

    Listener().start_listening()