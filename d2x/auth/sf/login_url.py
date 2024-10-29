import sys
import os
from rich.console import Console
from d2x.auth.sf.auth_url import exchange_token, parse_sfdx_auth_url
from d2x.gen.sf.login_url import get_login_url_and_token
from d2x.ux.gh.actions import summary, output


def main():
    """Main CLI entrypoint"""
    console = Console()

    try:
        auth_url = os.environ.get("SFDX_AUTH_URL")

        if not auth_url:
            raise ValueError(
                "Salesforce Auth Url not found. Set the SFDX_AUTH_URL environment variable."
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
        summary(error_md)
        sys.exit(1)


if __name__ == "__main__":
    main()
