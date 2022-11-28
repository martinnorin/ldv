"""Module for handling authentication cli commands"""

import click

from ldv.constants.remote import (
    RemoteStorageConstants as RSC
)

@click.group()
def auth():
    """Authentication commands"""
    pass  # pylint: disable=unnecessary-pass

@auth.command(name="aws")
@click.option("--region-name", "-rn", required=True)
@click.option(
    "--profile-name",
    "-pn",
    help="Profile specified in ~/.aws/config")
@click.option(
    "--environment-credentials",
    "-ec",
    default=False,
    is_flag=True,
    help="Use credentials stored in environment variables. "
         f"{RSC.LDV_AWS_ACCESS_KEY_ID} and "
         f"{RSC.LDV_AWS_SECRET_ACCESS_KEY} "
         "must be set. "
         "Will not be used if profile is provided.")
def aws(
    region_name: str,
    profile_name: str = None,
    environment_credentials: bool = False
):
    """AWS authentication

    Authentication can be done by using temporary credentials stored in
    profile in ~/.aws/config, or by using credentials stored in environment
    variables."""
    from ldv.remote.auth.aws import AwsAuth

    AwsAuth().store_auth(
        profile_name=profile_name,
        env_credentials=environment_credentials,
        region_name=region_name
    )