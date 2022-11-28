"""Module for handling versioning cli commands"""

import click

from ldv.core.versioning import Versioning

@click.group()
def versioning():
    """Versioning commands"""
    pass  # pylint: disable=unnecessary-pass

@versioning.command(name="track")
@click.argument("filepath")
@click.option(
    "--dont-upload",
    "-du",
    default=None,
    is_flag=True,
    help="Don't upload file to remote after version tracking")
def track(filepath, dont_upload):
    """ Version track file.

    \b
    Args:
        filepath: filepath to version track.
                  Can be absolute or relative path but must be under
                  path provided when running 'init' command.
        dont_upload: optional flag used to not upload file when tracking it.

    """

    upload = None
    if dont_upload:
        upload = not dont_upload
    Versioning().track(
        filepath=filepath,
        upload=upload
    )

@versioning.command(name="track-all")
@click.option(
    "--dont-upload",
    "-du",
    default=None,
    is_flag=True,
    help="Don't upload file to remote after version tracking")
def track_all(dont_upload):
    """ Version track all files under path specified in 'init' command.

    \b
    Args:
        dont_upload: optional flag used to not upload file when tracking it.
    """

    upload = None
    if dont_upload:
        upload = not dont_upload
    Versioning().track_all(upload=upload)

@versioning.command(name="download")
@click.argument("digest_filepath")
@click.option("--version", "-v", help="Optional version of file")
def download(digest_filepath: str, version: str = None):
    """ Download file with optional version.

    If no version is specified, it will use the version in the
    .digest file.

    \b
    Args:
        digest_filepath: filepath to download.
                  Can be absolute or relative but must
                  be under path specified in 'init' command. Also, it must have
                  .digest ending.
        version: optional version. If not provided, the version
                 in the .digest file will be used.

    """

    Versioning().download(
        digest_filepath=digest_filepath,
        version=version
    )

@versioning.command(name="download-all")
def download_all():
    """ Download all files under folder specified in .ldv/config. """

    Versioning().download_all()

@versioning.command(name="list-versions")
@click.argument("digest-filepath")
def list_versions(digest_filepath: str):
    """List versions of file

    Args:
        digest_filepath (str): filepath of digest file
    """

    versions: dict = Versioning().get_versions(digest_filepath=digest_filepath)
    print(f"Filename: {versions['relative_filepath']}")
    for version_item in versions["versions"]:
        version: str = version_item["version"]
        last_modified: str = version_item["last_modified"]
        size: str = version_item["size"]
        print(f"Version: {version}. Last modified: {last_modified}. Size: {size} B")
