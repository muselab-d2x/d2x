# auth.py

import urllib.parse
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional, Literal
from pydantic import BaseModel, Field, SecretStr, computed_field
from rich.table import Table
from rich import box
from d2x.base.models import CommonBaseModel

# Remove OutputFormatType import if not used
# from d2x.base.types import OutputFormatType


class OrgType(str, Enum):
    PRODUCTION = "production"
    SANDBOX = "sandbox"
    SCRATCH = "scratch"
    DEVELOPER = "developer"
    DEMO = "demo"


class DomainType(str, Enum):
    POD = "pod"
    LIGHTNING = "lightning"
    MY = "my"


class AuthInfo(CommonBaseModel):
    """Authentication components for Salesforce org."""

    client_id: str
    client_secret: str
    refresh_token: str
    instance_url: str


class TokenRequest(BaseModel):
    """OAuth token request parameters for Salesforce authentication"""

    grant_type: str = Field(
        default="refresh_token",
        description="OAuth grant type, always 'refresh_token' for this flow",
        pattern="^refresh_token$",  # Changed from regex to pattern
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
        pattern="^Bearer$",  # Changed from regex to pattern
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


class LoginUrlModel(CommonBaseModel):
    """Model to generate login URL and token"""

    access_token: str
    login_url: str
    ret_url: str = "/"

    def get_login_url_and_token(self) -> tuple[str, str]:
        """Generate login URL and token"""
        ret_url_encoded = urllib.parse.quote(self.ret_url)
        login_url_formatted = (
            f"{self.login_url}/secur/frontdoor.jsp?sid={self.access_token}&retURL={ret_url_encoded}"
        )
        return login_url_formatted, self.access_token


class SfdxAuthUrlModel(CommonBaseModel):
    """Model to parse SFDX auth URL"""

    auth_url: str

    def parse_sfdx_auth_url(self) -> dict:
        """Parse SFDX auth URL and extract detailed org information"""
        sfdx_auth_url_pattern = re.compile(
            r"^force://"
            r"(?P<client_id>[a-zA-Z0-9]{0,64})"
            r":"
            r"(?P<client_secret>[a-zA-Z0-9._~\-]*)"
            r":"
            r"(?P<refresh_token>[a-zA-Z0-9._~\-]+)"
            r"@"
            r"(?P<instance_url>"
            r"(?:https?://)?"
            r"(?P<mydomain>[a-zA-Z0-9\-]+)?"
            r"(?:--(?P<sandbox_name>[a-zA-Z0-9\-]+))?"
            r"(?:(?P<org_suffix>sandbox|scratch|developer|demo)?\.my\.salesforce\.com"
            r"|\.lightning\.force\.com"
            r"|\.my\.salesforce.com"
            r"|(?P<pod_type>cs|db)"
            r"|(?P<region>(?:na|eu|ap|au|uk|in|de|jp|sg|ca|br|fr|ae|il))"
            r")"
            r"(?P<pod_number>[0-9]+)?"
            r"(?:\.salesforce\.com)?"
            r")$"
        )

        match = sfdx_auth_url_pattern.match(self.auth_url)
        if not match:
            raise ValueError("Invalid SFDX auth URL format")

        groups = match.groupdict()

        org_type = OrgType.PRODUCTION
        if groups.get("org_suffix"):
            org_type = OrgType(groups["org_suffix"])
        elif groups.get("sandbox_name"):
            org_type = OrgType.SANDBOX

        domain_type = DomainType.POD
        if ".my.salesforce.com" in groups["instance_url"]:
            domain_type = DomainType.MY
        elif ".lightning.force.com" in groups["instance_url"]:
            domain_type = DomainType.LIGHTNING

        auth_info = AuthInfo(
            client_id=groups["client_id"],
            client_secret=groups["client_secret"] or "",
            refresh_token=groups["refresh_token"],
            instance_url=groups["instance_url"],
        )

        return {
            "auth_info": auth_info,
            "org_type": org_type,
            "domain_type": domain_type,
            "full_domain": groups["instance_url"],
            "region": groups.get("region"),
            "pod_number": groups.get("pod_number"),
            "pod_type": groups.get("pod_type"),
            "mydomain": groups.get("mydomain"),
            "sandbox_name": groups.get("sandbox_name"),
        }
