from typing import Optional, Literal
from pydantic import Field
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


class SalesforceOrgInfo(CommonBaseModel):
    """Structured information about a Salesforce org."""

    auth_info: AuthInfo = Field(
        ..., description="Authentication information for the Salesforce org."
    )
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

    @property
    def is_classic_pod(self) -> bool:
        """Determine if the pod is a classic pod."""
        return self.pod_type in ["cs", "db"]

    @property
    def is_hyperforce(self) -> bool:
        """Determine if the org is on Hyperforce."""
        return False  # Placeholder implementation

    @property
    def is_sandbox(self) -> bool:
        """Determine if the org is a sandbox."""
        return self.org_type == OrgType.SANDBOX
