import sys
import os
from rich.console import Console
from d2x.models.sf.auth import LoginUrlModel, SfdxAuthUrlModel
from d2x.ux.gh.actions import summary, output
from d2x.base.types import CLIOptions
from typing import Optional
from d2x.api.gh import get_environment_variable  # Add get_environment_variable import


def generate_login_url(instance_url: str, access_token: str) -> str:
    """Generate the login URL using the instance URL and access token."""
    login_url, _ = LoginUrlModel(
        access_token=access_token, login_url=instance_url
    ).get_login_url_and_token()
    return login_url


def main(cli_options: CLIOptions):
    """Main CLI entrypoint"""
    console = cli_options.console

    auth_url = os.environ.get("SFDX_AUTH_URL")

    if not auth_url:
        raise ValueError(
            "Salesforce Auth Url not found. Set the SFDX_AUTH_URL environment variable."
        )

    org_info = SfdxAuthUrlModel(auth_url=auth_url).parse_sfdx_auth_url()

    from d2x.auth.sf.auth_url import exchange_token

    try:
        access_token = get_environment_variable("salesforce", "ACCESS_TOKEN")
    except Exception as e:
        console.print(f"[red]Error retrieving access token: {e}")
        sys.exit(1)

    start_url = generate_login_url(
        instance_url=org_info.auth_info.instance_url,
        access_token=access_token,
    )

    output("access_token", access_token)  # Use access_token directly
    output("instance_url", org_info.auth_info.instance_url)

    output("start_url", start_url)
    output("org_type", org_info["org_type"])

    if org_info["domain_type"] == "pod":
        output("region", org_info["region"] or "classic")
        output("is_hyperforce", str(org_info["is_hyperforce"]).lower())

    from d2x.auth.sf.auth_url import get_full_domain

    summary_md = f"""
## Salesforce Authentication Successful 🚀

### Organization Details
- **Domain**: {get_full_domain(org_info)}
- **Type**: {org_info["org_type"]}
{"- **Region**: " + (org_info["region"] or "Classic") if org_info["domain_type"] == 'pod' else ""}
{"- **Hyperforce**: " + ("Yes" if org_info["is_hyperforce"] else "No") if org_info["domain_type"] == 'pod' else ""}

### Authentication Status
- **Status**: ✅ Success
- **Timestamp**: {token_response.issued_at.strftime('%Y-%m-%d %H:%M:%S')}
- **Token Expiry**: {token_response.expires_in} seconds
- **Instance URL**: {org_info.auth_info.instance_url}
"""
    summary(summary_md)

    console.print("\n[green]✓ Successfully authenticated to Salesforce!")
    console.print(f"\n[yellow]Login URL:[/]\n{start_url}")


if __name__ == "__main__":
    main()
