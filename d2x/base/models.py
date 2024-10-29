from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timedelta

class CommonBaseModel(BaseModel):
    """Common base class for all models"""

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        use_enum_values = True

    def to_dict(self):
        """Convert model to dictionary"""
        return self.dict(by_alias=True)

    def to_json(self):
        """Convert model to JSON string"""
        return self.json(by_alias=True)

    def to_yaml(self):
        """Convert model to YAML string"""
        try:
            import yaml
        except ImportError:
            raise ImportError("PyYAML is not installed. Please install it to use this method.")
        return yaml.dump(self.dict(by_alias=True))

    @classmethod
    def from_yaml(cls, yaml_str: str):
        """Create model instance from YAML string"""
        try:
            import yaml
        except ImportError:
            raise ImportError("PyYAML is not installed. Please install it to use this method.")
        data = yaml.safe_load(yaml_str)
        return cls(**data)

    @classmethod
    def from_dict(cls, data: dict):
        """Create model instance from dictionary"""
        return cls(**data)

    @classmethod
    def from_json(cls, json_str: str):
        """Create model instance from JSON string"""
        return cls.parse_raw(json_str)

    def to_openapi_schema(self):
        """Convert model to OpenAPI 3.1 schema"""
        return self.schema_json(by_alias=True)

class TokenRequest(CommonBaseModel):
    """OAuth token request parameters for Salesforce authentication"""

    grant_type: str = Field(
        default="refresh_token",
        description="OAuth grant type, always 'refresh_token' for this flow",
    )
    client_id: str = Field(
        description="The connected app's client ID/consumer key",
        examples=["PlatformCLI", "3MVG9..."],
    )
    client_secret: Optional[str] = Field(
        default=None,
        description="The connected app's client secret/consumer secret if required",
    )
    refresh_token: str = Field(
        description="The SFDX refresh token obtained from auth URL"
    )

    def to_form(self) -> str:
        """Convert to URL encoded form data, only including client_secret if provided"""
        data = {
            "grant_type": self.grant_type,
            "client_id": self.client_id,
            "refresh_token": self.refresh_token,
        }
        # Only include client_secret if it's provided
        if self.client_secret:
            data["client_secret"] = self.client_secret

        return urllib.parse.urlencode(data)

class TokenResponse(CommonBaseModel):
    """Salesforce OAuth token response"""

    access_token: str = Field(description="The OAuth access token for API calls")
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
    id_token: Optional[str] = Field(
        default=None, description="OpenID Connect ID token if requested"
    )

    @property
    def expires_at(self) -> datetime:
        """Calculate token expiration time"""
        return self.issued_at.replace(microsecond=0) + timedelta(
            seconds=self.expires_in
        )

    def model_dump_safe(self) -> dict:
        """Dump model while masking sensitive fields"""
        data = self.dict()
        data["access_token"] = "**********" + self.access_token[-4:]
        if self.id_token:
            data["id_token"] = "*" * 10
        return data

class HttpResponse(CommonBaseModel):
    """HTTP response details"""

    status: int = Field(description="HTTP status code", ge=100, le=599)
    reason: str = Field(description="HTTP status reason phrase")
    headers: dict[str, str] = Field(description="HTTP response headers")
    body: str = Field(description="Raw response body")
    parsed_body: Optional[dict] = Field(
        default=None, description="Parsed JSON response body if available"
    )

class TokenExchangeDebug(CommonBaseModel):
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
                "*" * len(self.request.client_secret)
                if self.request.client_secret
                else "Not provided"
            ),
        )
        table.add_row(
            "Refresh Token",
            "*" * 10 + self.request.refresh_token[-4:],
        )

        return table
