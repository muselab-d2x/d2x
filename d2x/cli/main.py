# cli.py
import rich_click as click
from d2x.auth.sf.login_url import main as login_url_main
from d2x.auth.sf.auth_url import main as auth_url_main
import sys
import pdb
from d2x.base.types import OutputFormat, OutputFormatType, CLIOptions
from typing import Optional
from importlib.metadata import version, PackageNotFoundError

# Disable rich_click's syntax highlighting
click.SHOW_ARGUMENTS = False
click.SHOW_METAVARS_COLUMN = False
click.SHOW_OPTIONS = False

try:
    VERSION = version("d2x")
except PackageNotFoundError:
    VERSION = "dev"


def common_options(func):
    """Decorator to add common options to all commands."""
    func = click.option(
        "--output-format",
        type=click.Choice([format.value for format in OutputFormat]),
        default=OutputFormat.TEXT.value,
        help="Output format.",
    )(func)
    func = click.option("--debug", is_flag=True, help="Enable debug mode.")(func)
    return func


@click.group(name="d2x")
@click.version_option(version=VERSION, prog_name="d2x")
def d2x_cli():
    """D2X CLI main command group"""
    pass


@d2x_cli.group()
def sf():
    """Salesforce commands"""
    pass


@sf.group()
def auth():
    """Salesforce authentication commands"""
    pass


@auth.command()
@common_options
def login(output_format: OutputFormatType, debug: bool):
    """Exchange Salesforce refresh token for a current login session start url."""
    cli_options = CLIOptions(output_format=output_format, debug=debug)
    try:
        login_url_main(cli_options)
    except:
        if debug:
            type, value, tb = sys.exc_info()
            pdb.post_mortem(tb)
        else:
            raise


@auth.command()
@common_options
def url(output_format: OutputFormatType, debug: bool):
    """Exchange SFDX_AUTH_URL for a Salesfoce access token session"""
    cli_options = CLIOptions(output_format=output_format, debug=debug)
    try:
        auth_url_main(cli_options)
    except:
        if debug:
            type, value, tb = sys.exc_info()
            pdb.post_mortem(tb)
        else:
            raise


def get_cli():
    """Get the CLI entry point"""
    return d2x_cli


if __name__ == "__main__":
    d2x_cli()
