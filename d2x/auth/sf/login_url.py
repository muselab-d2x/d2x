import sys
import os
from rich.console import Console
from d2x.gen.sf.login_url import get_login_url_and_token
from d2x.ux.gh.actions import summary, output
from d2x.base.types import CLIOptions
from typing import Optional
from d2x.auth.sf.auth_url import parse_sfdx_auth_url  # Add this import


def generate_login_url(instance_url: str, access_token: str) -> str:
    """Generate the login URL using the instance URL and access token."""
    login_url, _ = get_login_url_and_token(
        access_token=access_token, login_url=instance_url
    )
    return login_url


def main(cli_options: CLIOptions):
    """Main CLI entrypoint"""
    console = cli_options.console

    auth_url = os.environ.get("SFDX_AUTH_URL")

    if not auth_url:
        raise ValueError(
            "Salesforce Auth Url not found. Set the SFDX_AUTH_URL environment variable."
        )

    # Remove the console.status context manager
    # with console.status("[bold blue]Authenticating to Salesforce..."):
    #     # Parse and validate the auth URL
    #     from d2x.auth.sf.auth_url import parse_sfdx_auth_url

    org_info = parse_sfdx_auth_url(auth_url)

    # Exchange tokens
    from d2x.auth.sf.auth_url import exchange_token

    try:
        token_response = exchange_token(org_info, cli_options)
    except Exception as e:
        console.print(f"[red]Error: {e}")
        sys.exit(1)

    # Generate login URL
    start_url = generate_login_url(
        instance_url=token_response.instance_url,
        access_token=token_response.access_token.get_secret_value(),
    )

    # Set outputs for GitHub Actions
    output("access_token", token_response.access_token.get_secret_value())
    output("instance_url", token_response.instance_url)
    output("start_url", start_url)
    output("org_type", org_info.org_type)

    if org_info.domain_type == "pod":
        output("region", org_info.region or "classic")
        output("is_hyperforce", str(org_info.is_hyperforce).lower())

    # Add summary for GitHub Actions
    from d2x.auth.sf.auth_url import get_full_domain

    summary_md = f"""
## Salesforce Authentication Successful 🚀

### Organization Details
- **Domain**: {get_full_domain(org_info)}
- **Type**: {org_info.org_type}
{"- **Region**: " + (org_info.region or "Classic") if org_info.domain_type == 'pod' else ""}
{"- **Hyperforce**: " + ("Yes" if org_info.is_hyperforce else "No") if org_info.domain_type == 'pod' else ""}

### Authentication Status
- **Status**: ✅ Success
- **Timestamp**: {token_response.issued_at.strftime('%Y-%m-%d %H:%M:%S')}
- **Token Expiry**: {token_response.expires_in} seconds
- **Instance URL**: {token_response.instance_url}
"""
    summary(summary_md)

    # Success output
    console.print("\n[green]✓ Successfully authenticated to Salesforce!")
    console.print(f"\n[yellow]Login URL:[/]\n{start_url}")


if __name__ == "__main__":
    main()
