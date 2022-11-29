import click

from ldv.commands.auth import auth
from ldv.commands.versioning import versioning
from ldv.commands.init import init
from ldv.commands.listener import listener

@click.group()
def cli():
    """ Light data versioning. Is used for version tracking data. """

    pass

cli.add_command(auth)
cli.add_command(versioning)
cli.add_command(init)
cli.add_command(listener)

if __name__ == "__main__":
    cli()