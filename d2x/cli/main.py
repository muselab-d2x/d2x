import rich_click as click
from d2x.auth.sf.login_url import main as login_url_main
from d2x.auth.sf.auth_url import main as auth_url_main
import sys
import pdb
from d2x.base.types import OutputFormat, OutputFormatType, CLIOptions
from typing import Optional

# Disable rich_click's syntax highlighting
click.SHOW_ARGUMENTS = False
click.SHOW_METAVARS_COLUMN = False
click.SHOW_OPTIONS = False


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


@click.group()
@click.pass_context
def d2x_cli(ctx):
    ctx.ensure_object(dict)


@d2x_cli.command()
@common_options
@click.pass_context
def login_url(ctx, output_format: OutputFormatType, debug: bool):
    """Handle login URL command."""
    cli_options = CLIOptions(output_format=output_format, debug=debug)
    ctx.obj["CLI_OPTIONS"] = cli_options
    try:
        login_url_main(cli_options)
    except:
        if cli_options.debug:
            type, value, tb = sys.exc_info()
            pdb.post_mortem(tb)
        else:
            raise


@d2x_cli.command()
@common_options
@click.pass_context
def auth_url(ctx, output_format: OutputFormatType, debug: bool):
    """Handle auth URL command."""
    cli_options = CLIOptions(output_format=output_format, debug=debug)
    ctx.obj["CLI_OPTIONS"] = cli_options
    try:
        auth_url_main(cli_options)
    except:
        if cli_options.debug:
            type, value, tb = sys.exc_info()
            pdb.post_mortem(tb)
        else:
            raise


if __name__ == "__main__":
    d2x_cli()
