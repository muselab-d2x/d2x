import sys
import os
from rich.console import Console
from d2x.auth.sf_auth_url import exchange_token, parse_sfdx_auth_url
from d2x.auth.sf_login_url import generate_login_url
from d2x.gh.actions.ux import summary, output


def main():
    """Main CLI entrypoint"""
    console = Console()

    if len(sys.argv) < 2:
        console.print("[red]Error: No authentication URL provided")
        console.print("Usage: d2x auth login --url <sfdx_auth_url>")
        sys.exit(1)

    try:
        # Get auth URL from args or env
        auth_url = None
        if "--url" in sys.argv:
            url_index = sys.argv.index("--url") + 1
            if url_index < len(sys.argv):
                auth_url = sys.argv[url_index]

        if not auth_url:
            auth_url = os.environ.get("SFDX_AUTH_URL")

        if not auth_url:
            raise ValueError(
                "No authentication URL provided via --url or SFDX_AUTH_URL"
            )

        # Execute the login flow
        with console.status("[bold blue]Authenticating to Salesforce..."):
            # Parse and validate the auth URL
            org_info = parse_sfdx_auth_url(auth_url)

            # Exchange tokens
            token_response = exchange_token(org_info, console)

            # Generate login URL
            start_url = generate_login_url(
                instance_url=token_response.instance_url,
                access_token=token_response.access_token.get_secret_value(),
            )

            # Set outputs for GitHub Actions
            output.add("access_token", token_response.access_token.get_secret_value())
            output.add("instance_url", token_response.instance_url)
            output.add("start_url", start_url)
            output.add("org_type", org_info.org_type)

            if org_info.domain_type == "pod":
                output.add("region", org_info.region or "classic")
                output.add("is_hyperforce", str(org_info.is_hyperforce).lower())

            # Add summary for GitHub Actions
            summary_md = f"""
## Salesforce Authentication Successful 🚀

### Organization Details
- **Domain**: {org_info.full_domain}
- **Type**: {org_info.org_type}
{"- **Region**: " + (org_info.region or "Classic") if org_info.domain_type == 'pod' else ""}
{"- **Hyperforce**: " + ("Yes" if org_info.is_hyperforce else "No") if org_info.domain_type == 'pod' else ""}

### Authentication Status
- **Status**: ✅ Success
- **Timestamp**: {token_response.issued_at.strftime('%Y-%m-%d %H:%M:%S')}
- **Token Expiry**: {token_response.expires_in} seconds
- **Instance URL**: {token_response.instance_url}

### Quick Access
```
{start_url}
```
"""
            summary.add(summary_md)

            # Success output
            console.print("\n[green]✓ Successfully authenticated to Salesforce!")
            console.print(f"\n[yellow]Login URL:[/]\n{start_url}")

    except Exception as e:
        console.print(f"[red]Error: {str(e)}")
        error_md = f"""
## ❌ Authentication Failed

**Error**: {str(e)}
"""
        summary.add(error_md)
        sys.exit(1)


if __name__ == "__main__":
    main()
