import click

import ldv.core.init

@click.command(name="init")
@click.option("--path", "-p", required=True)
@click.option("--url", "-u", required=True)
@click.option(
    "--rerun-track-all",
    "-rta",
    default=False,
    is_flag=True,
    help="Re-run 'ldv versioning track-all' command to copy all "
         "version tracked files to new remote location"
)
@click.option(
    "--dont-upload",
    "-du",
    default=False,
    is_flag=True,
    help="Don't upload files to remote on version tracking. "
         "If flag is not provided, default is to upload files to remote"
)
def init(path: str, url: str, rerun_track_all: bool, dont_upload: bool):
    """Initialize root path and url for versioning

    \b
    Args:
        path (str): root path
        url (str): remote storage url
        dont_upload (bool): flag if upload should not be done
    """
    ldv.core.init.init(path=path, url=url, upload=not dont_upload)

    if rerun_track_all:
        from ldv.core.versioning import Versioning

        Versioning().track_all()