# cli.py
import rich_click as click
from d2x.models.sf.auth import LoginUrlModel, SfdxAuthUrlModel
import sys
import pdb
from d2x.base.types import OutputFormat, OutputFormatType, CLIOptions
from typing import Optional
from importlib.metadata import version, PackageNotFoundError
from d2x.env.gh import set_environment_variable, get_environment_variable, set_environment_secret, get_environment_secret
from d2x.auth.sf.auth_url import create_scratch_org, exchange_token
from d2x.models.sf.org import SalesforceOrgInfo, ScratchOrg

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


@sf.group()
def org():
    """Salesforce org commands"""
    pass


@org.command()
@common_options
def create(output_format: OutputFormatType, debug: bool):
    """Create a Salesforce scratch org"""
    cli_options = CLIOptions(output_format=output_format, debug=debug)
    try:
        # Assuming org_info is obtained from somewhere, e.g., environment variable or input
        org_info = ScratchOrg(
            org_type="scratch",
            domain_type="my",
            full_domain="example.my.salesforce.com",
            auth_info=AuthInfo(
                client_id="your_client_id",
                client_secret="your_client_secret",
                refresh_token="your_refresh_token",
                instance_url="https://example.my.salesforce.com",
            ),
        )
        create_scratch_org(org_info, cli_options)
    except:
        if debug:
            type, value, tb = sys.exc_info()
            pdb.post_mortem(tb)
        else:
            raise


@org.command()
@common_options
def exchange(output_format: OutputFormatType, debug: bool):
    """Exchange auth code for an OAuth grant"""
    cli_options = CLIOptions(output_format=output_format, debug=debug)
    try:
        # Assuming org_info is obtained from somewhere, e.g., environment variable or input
        org_info = SalesforceOrgInfo(
            auth_info=AuthInfo(
                client_id="your_client_id",
                client_secret="your_client_secret",
                refresh_token="your_refresh_token",
                instance_url="https://example.my.salesforce.com",
            ),
            org=ScratchOrg(
                org_type="scratch",
                domain_type="my",
                full_domain="example.my.salesforce.com",
            ),
        )
        exchange_token(org_info, cli_options)
    except:
        if debug:
            type, value, tb = sys.exc_info()
            pdb.post_mortem(tb)
        else:
            raise


@d2x_cli.group()
def env():
    """Environment commands"""
    pass


@env.command()
@click.argument("env_name")
@click.argument("var_name")
@click.argument("var_value")
@common_options
def set_var(env_name: str, var_name: str, var_value: str, output_format: OutputFormatType, debug: bool):
    """Set an environment variable"""
    cli_options = CLIOptions(output_format=output_format, debug=debug)
    try:
        set_environment_variable(env_name, var_name, var_value)
    except:
        if debug:
            type, value, tb = sys.exc_info()
            pdb.post_mortem(tb)
        else:
            raise


@env.command()
@click.argument("env_name")
@click.argument("var_name")
@common_options
def get_var(env_name: str, var_name: str, output_format: OutputFormatType, debug: bool):
    """Get an environment variable"""
    cli_options = CLIOptions(output_format=output_format, debug=debug)
    try:
        value = get_environment_variable(env_name, var_name)
        click.echo(value)
    except:
        if debug:
            type, value, tb = sys.exc_info()
            pdb.post_mortem(tb)
        else:
            raise


@env.command()
@click.argument("env_name")
@click.argument("secret_name")
@click.argument("secret_value")
@common_options
def set_secret(env_name: str, secret_name: str, secret_value: str, output_format: OutputFormatType, debug: bool):
    """Set an environment secret"""
    cli_options = CLIOptions(output_format=output_format, debug=debug)
    try:
        set_environment_secret(env_name, secret_name, secret_value)
    except:
        if debug:
            type, value, tb = sys.exc_info()
            pdb.post_mortem(tb)
        else:
            raise


@env.command()
@click.argument("env_name")
@click.argument("secret_name")
@common_options
def get_secret(env_name: str, secret_name: str, output_format: OutputFormatType, debug: bool):
    """Get an environment secret"""
    cli_options = CLIOptions(output_format=output_format, debug=debug)
    try:
        value = get_environment_secret(env_name, secret_name)
        click.echo(value)
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
