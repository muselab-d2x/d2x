from typing import Optional, Literal, Union
from pydantic import Field, BaseModel
from d2x.base.models import CommonBaseModel
from d2x.models.sf.auth import AuthInfo, DomainType, OrgType

RegionType = Literal[
    "na",
    "eu",
    "ap",
    "au",
    "uk",
    "in",
    "de",
    "jp",
    "sg",
    "ca",
    "br",
    "fr",
    "ae",
    "il",
    None,
]
PodType = Literal["cs", "db", None]


class BaseSalesforceOrg(BaseModel):
    """Base model for Salesforce orgs with a pydantic discriminator."""

    org_type: OrgType = Field(..., description="Type of the Salesforce org.")
    domain_type: DomainType = Field(
        ..., description="Type of domain for the Salesforce org."
    )
    full_domain: str = Field(..., description="Full domain of the Salesforce org.")
    mydomain: Optional[str] = Field(
        None, description="MyDomain name of the Salesforce org."
    )
    sandbox_name: Optional[str] = Field(None, description="Sandbox name if applicable.")
    region: Optional[RegionType] = Field(
        None, description="Region of the Salesforce org."
    )
    pod_number: Optional[str] = Field(None, description="Pod number if applicable.")
    pod_type: Optional[PodType] = Field(None, description="Pod type if applicable.")

    class Config:
        use_enum_values = True
        discriminator = "org_type"


class ProductionOrg(BaseSalesforceOrg):
    """Model for Production Salesforce orgs."""

    org_type: Literal[OrgType.PRODUCTION] = Field(
        default=OrgType.PRODUCTION, description="Type of the Salesforce org."
    )
    instance_url: str = Field(..., description="Instance URL of the production org.")
    created_date: str = Field(..., description="Creation date of the production org.")
    last_modified_date: str = Field(..., description="Last modified date of the production org.")
    status: str = Field(..., description="Status of the production org.")


class TrialOrg(BaseSalesforceOrg):
    """Model for Trial Salesforce orgs."""

    org_type: Literal[OrgType.DEMO] = Field(
        default=OrgType.DEMO, description="Type of the Salesforce org."
    )
    expiration_date: Optional[str] = Field(
        None, description="Expiration date of the trial org."
    )
    instance_url: str = Field(..., description="Instance URL of the trial org.")
    created_date: str = Field(..., description="Creation date of the trial org.")
    last_modified_date: str = Field(..., description="Last modified date of the trial org.")
    status: str = Field(..., description="Status of the trial org.")


class SandboxOrg(BaseSalesforceOrg):
    """Model for Sandbox Salesforce orgs."""

    org_type: Literal[OrgType.SANDBOX] = Field(
        default=OrgType.SANDBOX, description="Type of the Salesforce org."
    )
    instance_url: str = Field(..., description="Instance URL of the sandbox org.")
    created_date: str = Field(..., description="Creation date of the sandbox org.")
    last_modified_date: str = Field(..., description="Last modified date of the sandbox org.")
    status: str = Field(..., description="Status of the sandbox org.")


class ScratchOrg(BaseSalesforceOrg):
    """Model for Scratch Salesforce orgs."""

    org_type: Literal[OrgType.SCRATCH] = Field(
        default=OrgType.SCRATCH, description="Type of the Salesforce org."
    )
    expiration_date: Optional[str] = Field(
        None, description="Expiration date of the scratch org."
    )
    instance_url: str = Field(..., description="Instance URL of the scratch org.")
    created_date: str = Field(..., description="Creation date of the scratch org.")
    last_modified_date: str = Field(..., description="Last modified date of the scratch org.")
    status: str = Field(..., description="Status of the scratch org.")


class SalesforceOrgInfo(CommonBaseModel):
    """Structured information about a Salesforce org."""

    auth_info: AuthInfo = Field(
        ..., description="Authentication information for the Salesforce org."
    )
    org: Union[ProductionOrg, TrialOrg, SandboxOrg, ScratchOrg] = Field(
        ..., description="Salesforce org details."
    )

    @property
    def is_classic_pod(self) -> bool:
        """Determine if the pod is a classic pod."""
        return self.org.pod_type in ["cs", "db"]

    @property
    def is_hyperforce(self) -> bool:
        """Determine if the org is on Hyperforce."""
        return False  # Placeholder implementation

    @property
    def is_sandbox(self) -> bool:
        """Determine if the org is a sandbox."""
        return self.org.org_type == OrgType.SANDBOX
