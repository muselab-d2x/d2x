# Standard library imports
import http.client
import json
import os
import sys
import urllib.parse
from datetime import datetime, timedelta
from typing import Optional, Literal

# Third party imports
from pydantic import BaseModel, Field, SecretStr, computed_field
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

# Local imports
from d2x.parse.sf.auth_url import parse_sfdx_auth_url, SalesforceOrgInfo
from d2x.ux.gh.actions import summary as gha_summary, output as gha_output


# Type definitions
OrgType = Literal["production", "sandbox", "scratch", "developer", "demo"]
DomainType = Literal["my", "lightning", "pod"]


class TokenRequest(BaseModel):
    """OAuth token request parameters for Salesforce authentication"""

    grant_type: str = Field(
        default="refresh_token",
        description="OAuth grant type, always 'refresh_token' for this flow",
    )
    client_id: str = Field(
        description="The connected app's client ID/consumer key",
        examples=["PlatformCLI", "3MVG9..."],
    )
    client_secret: Optional[SecretStr] = Field(
        default=None,
        description="The connected app's client secret/consumer secret if required",
    )
    refresh_token: SecretStr = Field(
        description="The SFDX refresh token obtained from auth URL"
    )

    def to_form(self) -> str:
        """Convert to URL encoded form data, only including client_secret if provided"""
        data = {
            "grant_type": self.grant_type,
            "client_id": self.client_id,
            "refresh_token": self.refresh_token.get_secret_value(),
        }
        # Only include client_secret if it's provided
        if self.client_secret:
            data["client_secret"] = self.client_secret.get_secret_value()

        return urllib.parse.urlencode(data)


class TokenResponse(BaseModel):
    """Salesforce OAuth token response"""

    access_token: SecretStr = Field(description="The OAuth access token for API calls")
    instance_url: str = Field(
        description="The Salesforce instance URL for API calls",
        examples=["https://mycompany.my.salesforce.com"],
    )
    issued_at: datetime = Field(
        default_factory=datetime.now, description="Timestamp when the token was issued"
    )
    expires_in: int = Field(
        default=7200, description="Token lifetime in seconds", ge=0, examples=[7200]
    )
    token_type: str = Field(
        default="Bearer",
        description="OAuth token type, typically 'Bearer'",
        pattern="^Bearer$",
    )
    scope: Optional[str] = Field(
        default=None, description="OAuth scopes granted to the token"
    )
    signature: Optional[str] = Field(
        default=None, description="Request signature for verification"
    )
    id_token: Optional[SecretStr] = Field(
        default=None, description="OpenID Connect ID token if requested"
    )

    @computed_field
    def expires_at(self) -> datetime:
        """Calculate token expiration time"""
        return self.issued_at.replace(microsecond=0) + timedelta(
            seconds=self.expires_in
        )

    def model_dump_safe(self) -> dict:
        """Dump model while masking sensitive fields"""
        data = self.model_dump()
        data["access_token"] = "**********" + self.access_token.get_secret_value()[-4:]
        if self.id_token:
            data["id_token"] = "*" * 10
        return data


class HttpResponse(BaseModel):
    """HTTP response details"""

    status: int = Field(description="HTTP status code", ge=100, le=599)
    reason: str = Field(description="HTTP status reason phrase")
    headers: dict[str, str] = Field(description="HTTP response headers")
    body: str = Field(description="Raw response body")
    parsed_body: Optional[dict] = Field(
        default=None, description="Parsed JSON response body if available"
    )


class TokenExchangeDebug(BaseModel):
    """Debug information for token exchange"""

    url: str = Field(
        description="Full URL for token exchange request",
        examples=["https://login.salesforce.com/services/oauth2/token"],
    )
    method: str = Field(description="HTTP method used", pattern="^POST$")
    headers: dict[str, str] = Field(description="HTTP request headers")
    request: TokenRequest = Field(description="Token request parameters")
    response: Optional[HttpResponse] = Field(
        default=None, description="Response information when available"
    )
    error: Optional[str] = Field(
        default=None, description="Error message if exchange failed"
    )

    def to_table(self) -> Table:
        """Convert debug info to rich table"""
        table = Table(title="Token Exchange Details", box=box.ROUNDED)
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="yellow")

        table.add_row("URL", self.url)
        table.add_row("Method", self.method)
        for header, value in self.headers.items():
            table.add_row(f"Header: {header}", value)
        table.add_row("Client ID", self.request.client_id)
        table.add_row(
            "Client Secret",
            (
                "*" * len(self.request.client_secret.get_secret_value())
                if self.request.client_secret
                else "Not provided"
            ),
        )
        table.add_row(
            "Refresh Token",
            "*" * 10 + self.request.refresh_token.get_secret_value()[-4:],
        )

        return table


def exchange_token(org_info: SalesforceOrgInfo, console: Console) -> TokenResponse:
    """Exchange refresh token for access token with detailed error handling"""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        try:
            progress.add_task("Preparing token request...", total=None)

            # Create token request - only include client_secret if provided in URL
            token_request = TokenRequest(
                client_id=org_info.client_id,
                client_secret=(
                    SecretStr(org_info.client_secret)
                    if org_info.client_secret
                    else None
                ),
                refresh_token=SecretStr(org_info.refresh_token),
            )

            # Prepare the request
            token_url_path = "/services/oauth2/token"
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            body = token_request.to_form()

            # Create debug info
            debug = TokenExchangeDebug(
                url=f"https://{org_info.full_domain}{token_url_path}",
                method="POST",
                headers=headers,
                request=token_request,
            )

            console.print(debug.to_table())

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

            debug.response = http_response

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

            return token_response

        except Exception as e:
            debug.error = str(e)
            error_panel = Panel(
                f"[red]Error: {str(e)}",
                title="[red]Authentication Failed",
                border_style="red",
            )
            console.print(error_panel)
            raise


def main():
    console = Console(record=True)

    try:
        # Get auth URL from environment or args
        auth_url = os.environ.get("SFDX_AUTH_URL") or sys.argv[1]

        # Parse URL and display org info
        with console.status("[bold blue]Parsing SFDX Auth URL..."):
            org_info = parse_sfdx_auth_url(auth_url)

        table = Table(title="Salesforce Org Information", box=box.ROUNDED)
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Org Type", org_info.org_type)
        table.add_row("Domain Type", org_info.domain_type)
        table.add_row("Full Domain", org_info.full_domain)

        if org_info.domain_type == "pod":
            table.add_row("Region", org_info.region or "Classic")
            table.add_row("Pod Number", org_info.pod_number or "N/A")
            table.add_row("Pod Type", org_info.pod_type or "Standard")
            table.add_row("Is Classic Pod", "✓" if org_info.is_classic_pod else "✗")
            table.add_row("Is Hyperforce", "✓" if org_info.is_hyperforce else "✗")
        else:
            table.add_row("MyDomain", org_info.mydomain or "N/A")
            table.add_row("Sandbox Name", org_info.sandbox_name or "N/A")
            table.add_row("Is Sandbox", "✓" if org_info.is_sandbox else "✗")

        console.print(table)

        # Exchange token
        token_response = exchange_token(org_info, console)

        # Create step summary
        summary_md = f"""
## Salesforce Authentication Results

### Organization Details
- **Domain**: {org_info.full_domain}
- **Type**: {org_info.org_type}
{"- **Region**: " + (org_info.region or "Classic") if org_info.domain_type == 'pod' else ""}
{"- **Hyperforce**: " + ("Yes" if org_info.is_hyperforce else "No") if org_info.domain_type == 'pod' else ""}

### Authentication Status
- **Status**: ✅ Success
- **Timestamp**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Token Expiry**: {token_response.expires_in} seconds
        """
        gha_summary(summary_md)

        # Set action outputs
        gha_output("access_token", token_response.access_token.get_secret_value())
        gha_output("instance_url", token_response.instance_url)
        gha_output("org_type", org_info.org_type)
        if org_info.domain_type == "pod":
            gha_output("region", org_info.region or "classic")
            gha_output("is_hyperforce", str(org_info.is_hyperforce).lower())

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
    main()
