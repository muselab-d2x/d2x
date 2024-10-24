import re
from dataclasses import dataclass
from typing import Optional, Literal

# Define explicit type literals for better type hints
OrgType = Literal["production", "sandbox", "scratch", "developer", "demo"]
DomainType = Literal["my", "lightning", "pod"]
PodType = Literal["cs", "db", None]
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


@dataclass
class SalesforceOrgInfo:
    """Structured information about a Salesforce org parsed from SFDX auth URL"""

    # Auth components
    client_id: str
    client_secret: str
    refresh_token: str
    instance_url: str

    # Org identification
    org_type: OrgType
    domain_type: DomainType

    # Pod/Instance information
    region: RegionType
    pod_number: Optional[str]
    pod_type: PodType

    # MyDomain information
    mydomain: Optional[str]
    sandbox_name: Optional[str]  # The name after -- for sandbox/scratch orgs

    @property
    def is_classic_pod(self) -> bool:
        """Whether this is a classic pod (cs/db)"""
        return bool(self.pod_type in ("cs", "db"))

    @property
    def is_hyperforce(self) -> bool:
        """Whether this org is on Hyperforce based on region"""
        hyperforce_regions = {
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
        }
        return bool(self.region and self.region.lower() in hyperforce_regions)

    @property
    def is_sandbox(self) -> bool:
        """Whether this is a sandbox org"""
        return self.org_type in ("sandbox", "scratch", "developer", "demo")

    @property
    def full_domain(self) -> str:
        """Reconstructed full domain without protocol"""
        if self.domain_type == "pod":
            base = f"{self.region or self.pod_type}{self.pod_number}"
            return f"{base}.salesforce.com"
        elif self.domain_type == "lightning":
            return f"{self.mydomain}.lightning.force.com"
        else:  # my
            base = f"{self.mydomain}"
            if self.sandbox_name:
                base = f"{base}--{self.sandbox_name}"
            if self.org_type != "production":
                return f"{base}.{self.org_type}.my.salesforce.com"
            return f"{base}.my.salesforce.com"


# Updated regex pattern for better metadata extraction
sfdx_auth_url_pattern = re.compile(
    r"^force://"  # Protocol prefix
    r"(?P<client_id>[a-zA-Z0-9]{0,64})"  # Client ID: alphanumeric, 0-64 chars
    r":"  # Separator
    r"(?P<client_secret>[a-zA-Z0-9._~\-]*)"  # Client secret: optional
    r":"  # Separator
    r"(?P<refresh_token>[a-zA-Z0-9._~\-]+)"  # Refresh token: required
    r"@"  # Separator for instance URL
    r"(?P<instance_url>"  # Instance URL group
    r"(?:https?://)?"  # Protocol is optional
    r"(?:"  # Start non-capturing group for all possible domains
    r"(?:"  # Domain patterns group
    # MyDomain with optional sandbox/scratch org
    r"(?P<mydomain>[a-zA-Z0-9\-]+)"  # Base domain
    r"(?:--(?P<sandbox_name>[a-zA-Z0-9\-]+))?"  # Optional sandbox name
    r"(?:"  # Start non-capturing group for domain types
    r"\.(?P<org_suffix>sandbox|scratch|developer|demo)?\.my\.salesforce\.com"  # .my.salesforce.com domains
    r"|"
    r"\.lightning\.force\.com"  # lightning.force.com domains
    r"|"
    r"\.my\.salesforce\.com"  # Regular my.salesforce.com
    r")"
    r"|"  # OR
    r"(?P<pod_type>cs|db)"  # Classic pods (cs/db)
    r"|"  # OR
    r"(?P<region>(?:na|eu|ap|au|uk|in|de|jp|sg|ca|br|fr|ae|il))"  # Region codes
    r")"
    r"(?P<pod_number>[0-9]+)?"  # Optional pod number
    r"(?:\.salesforce\.com)?"  # Domain suffix for non-lightning domains
    r")"
    r")$"
)


def parse_sfdx_auth_url(auth_url: str) -> SalesforceOrgInfo:
    """Parse an SFDX auth URL and extract detailed org information"""
    match = sfdx_auth_url_pattern.match(auth_url)
    if not match:
        raise ValueError("Invalid SFDX auth URL format")

    groups = match.groupdict()

    # Determine org type
    org_type: OrgType = "production"
    if groups.get("org_suffix"):
        org_type = groups["org_suffix"]  # type: ignore
    elif groups.get("sandbox_name"):
        org_type = "sandbox"

    # Determine domain type
    domain_type: DomainType = "pod"
    if ".my.salesforce.com" in groups["instance_url"]:
        domain_type = "my"
    elif ".lightning.force.com" in groups["instance_url"]:
        domain_type = "lightning"

    return SalesforceOrgInfo(
        # Auth components
        client_id=groups["client_id"],
        client_secret=groups["client_secret"] or "",
        refresh_token=groups["refresh_token"],
        instance_url=groups["instance_url"],
        # Org identification
        org_type=org_type,
        domain_type=domain_type,
        # Pod/Instance information
        region=groups.get("region"),  # type: ignore
        pod_number=groups.get("pod_number"),
        pod_type=groups.get("pod_type"),  # type: ignore
        # MyDomain information
        mydomain=groups.get("mydomain"),
        sandbox_name=groups.get("sandbox_name"),
    )


def test_sfdx_auth_url_parser():
    test_urls = [
        "force://PlatformCLI::5Aep861T.BgtJABwpkWJm7RYLcqlS4pV50Iqxf8rqKD4F09oWzHo1vYJpfDnO0YpZ5lNfgw6wqUVShF2qVS2oSh@platypus-aries-9947-dev-ed.scratch.my.salesforce.com",
        "force://PlatformCLI::token123@https://mycompany.my.salesforce.com",
        "force://PlatformCLI::token123@https://mycompany.lightning.force.com",
        "force://PlatformCLI::token123@https://mycompany--dev.sandbox.my.salesforce.com",
        "force://PlatformCLI::token123@https://cs89.salesforce.com",
        "force://PlatformCLI::token123@https://na139.salesforce.com",
        "force://PlatformCLI::token123@https://au5.salesforce.com",
    ]

    print("\nTesting SFDX Auth URL Parser:")
    print("-" * 50)

    for url in test_urls:
        try:
            info = parse_sfdx_auth_url(url)
            print(f"\nParsed URL: {url[:50]}...")
            print(f"Full Domain: {info.full_domain}")
            print(f"Org Type: {info.org_type}")
            print(f"Domain Type: {info.domain_type}")
            if info.domain_type == "pod":
                print(f"Pod Details:")
                print(f"  Region: {info.region or 'Classic'}")
                print(f"  Number: {info.pod_number}")
                print(f"  Type: {info.pod_type or 'Standard'}")
                print(f"  Classic: {info.is_classic_pod}")
                print(f"  Hyperforce: {info.is_hyperforce}")
            else:
                print(f"MyDomain: {info.mydomain}")
                if info.sandbox_name:
                    print(f"Sandbox Name: {info.sandbox_name}")
                print(f"Is Sandbox: {info.is_sandbox}")
            print("-" * 30)
        except ValueError as e:
            print(f"Error parsing URL: {e}")


if __name__ == "__main__":
    test_sfdx_auth_url_parser()
