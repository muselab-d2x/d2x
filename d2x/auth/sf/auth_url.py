# Standard library imports
import http.client
import json
import os
import sys
import urllib.parse
from datetime import datetime, timedelta

# Third party imports
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

# Local imports
from d2x.models.sf.auth import (
    DomainType,
    TokenRequest,
    TokenResponse,
    HttpResponse,
    TokenExchangeDebug,
    SfdxAuthUrlModel,
)
from d2x.ux.gh.actions import summary as gha_summary, output as gha_output
from d2x.models.sf.org import SalesforceOrgInfo
from d2x.base.types import CLIOptions
from d2x.api.gh import set_environment_variable  # Add this import


def exchange_token(org_info: SalesforceOrgInfo, cli_options: CLIOptions):
    """Exchange refresh token for access token with detailed error handling"""
    console = cli_options.console
    debug_info = None  # Initialize debug_info before the try block
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        try:
            progress.add_task("Preparing token request...", total=None)

            # Create token request using auth_info
            token_request = TokenRequest(
                client_id=org_info.auth_info.client_id,
                client_secret=(
                    org_info.auth_info.client_secret.get_secret_value()
                    if org_info.auth_info.client_secret
                    else None
                ),
                refresh_token=org_info.auth_info.refresh_token,
            )

            # Prepare the request
            token_url_path = "/services/oauth2/token"
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            body = token_request.to_form()

            # Create debug info
            debug_info = TokenExchangeDebug(
                url=f"https://{org_info.full_domain}{token_url_path}",
                method="POST",
                headers=headers,
                request=token_request,
            )

            console.print(debug_info.to_table())

            # Make request
            progress.add_task(f"Connecting to {org_info.full_domain}...", total=None)
            conn = http.client.HTTPSConnection(org_info.full_domain)

            task = progress.add_task("Exchanging tokens...", total=None)
            conn.request("POST", token_url_path, body, headers)
            response = conn.getresponse()
            response_data = response.read()

            # Create response object
            http_response = HttpResponse(
                status=response.status,
                reason=response.reason,
                headers=dict(response.getheaders()),
                body=response_data.decode("utf-8"),
            )

            try:
                http_response.parsed_body = json.loads(http_response.body)
            except json.JSONDecodeError:
                pass

            debug_info.response = http_response

            if response.status != 200:
                error_panel = Panel(
                    f"[red]HTTP Status: {http_response.status} {http_response.reason}\n\n"
                    f"[yellow]Response Headers:[/]\n"
                    f"{http_response.headers}\n\n"
                    f"[yellow]Response Body:[/]\n"
                    f"{http_response.body}",
                    title="[red]Token Exchange Failed",
                    border_style="red",
                )
                console.print(error_panel)
                raise RuntimeError(
                    f"Token exchange failed: {response.status} {response.reason}"
                )

            progress.update(task, description="Token exchange successful!")

            # Parse token response
            token_response = TokenResponse.model_validate(http_response.parsed_body)

            # Display success
            success_panel = Panel(
                f"[green]Successfully authenticated to {org_info.full_domain}\n"
                f"[blue]Token Details:[/]\n"
                f"  Issued At: {token_response.issued_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"  Expires At: {token_response.expires_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"  ({token_response.expires_in} seconds)\n"
                f"[cyan]Instance URL: {token_response.instance_url}",
                title="[green]Authentication Success",
                border_style="green",
            )
            console.print(success_panel)

            # Store access token in GitHub Environment
            set_environment_variable("salesforce", "ACCESS_TOKEN", token_response.access_token.get_secret_value())

            return token_response

        except Exception as e:
            if debug_info is not None:
                debug_info.error = str(e)
            error_panel = Panel(
                f"[red]Error: {str(e)}",
                title="[red]Authentication Failed",
                border_style="red",
            )
            console.print(error_panel)
            raise


def get_full_domain(org_info: SalesforceOrgInfo) -> str:
    """Construct the full domain from SalesforceOrgInfo."""
    return org_info.full_domain.rstrip("/")


def main(cli_options: CLIOptions):
    """Main CLI entrypoint"""
    console = cli_options.console

    try:
        # Get auth URL from environment or args
        auth_url = os.environ.get("SFDX_AUTH_URL") or sys.argv[1]

        # Remove the console.status context manager
        # with console.status("[bold blue]Parsing SFDX Auth URL..."):
        #     org_info = parse_sfdx_auth_url(auth_url)
        org_info = SfdxAuthUrlModel(auth_url=auth_url).parse_sfdx_auth_url()

        table = Table(title="Salesforce Org Information", box=box.ROUNDED)
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Org Type", org_info["org_type"])
        table.add_row("Domain Type", org_info["domain_type"])
        table.add_row("Full Domain", org_info["full_domain"])

        if org_info["domain_type"] == DomainType.POD:
            table.add_row("Region", org_info["region"] or "Classic")
            table.add_row("Pod Number", org_info["pod_number"] or "N/A")
            table.add_row("Pod Type", org_info["pod_type"] or "Standard")
            table.add_row("Is Classic Pod", "✓" if org_info["is_classic_pod"] else "✗")
            table.add_row("Is Hyperforce", "✓" if org_info["is_hyperforce"] else "✗")
        else:
            table.add_row("MyDomain", org_info["mydomain"] or "N/A")
            table.add_row("Sandbox Name", org_info["sandbox_name"] or "N/A")
            table.add_row("Is Sandbox", "✓" if org_info["is_sandbox"] else "✗")

        console.print(table)

        # Exchange token
        token_response = exchange_token(org_info, cli_options)

        # Create step summary
        summary_md = f"""
## Salesforce Authentication Results

### Organization Details
- **Domain**: {org_info["full_domain"]}
- **Type**: {org_info["org_type"]}
{"- **Region**: " + (org_info["region"] or "Classic") if org_info["domain_type"] == DomainType.POD else ""}
{"- **Hyperforce**: " + ("Yes" if org_info["is_hyperforce"] else "No") if org_info["domain_type"] == DomainType.POD else ""}

### Authentication Status
- **Status**: ✅ Success
- **Timestamp**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Token Expiry**: {token_response.expires_in} seconds
        """
        gha_summary(summary_md)

        # Set action outputs
        gha_output("access_token", token_response.access_token)
        gha_output("instance_url", token_response.instance_url)
        gha_output("org_type", org_info["org_type"])
        if org_info["domain_type"] == DomainType.POD:
            gha_output("region", org_info["region"] or "classic")
            gha_output("is_hyperforce", str(org_info["is_hyperforce"]).lower())

        sys.exit(0)

    except Exception as e:
        # Create error panel
        error_panel = Panel(
            f"[red]Error: {str(e)}",
            title="[red]Authentication Failed",
            border_style="red",
        )
        console.print(error_panel)

        # Add error to job summary
        error_summary = f"""
## ❌ Authentication Failed

**Error**: {str(e)}
**Timestamp**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        gha_summary(error_summary)

        sys.exit(1)


if __name__ == "__main__":
    import sys
    from d2x.base.types import CLIOptions

    # Assuming CLIOptions is instantiated before calling main
    # This part is handled in cli.py
    pass
