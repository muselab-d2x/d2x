import re
from typing import Literal
from d2x.models.sf.org import SalesforceOrgInfo
from d2x.models.sf.auth import AuthInfo, OrgType, DomainType  # Add this import

# Remove the following Literal definitions:
# OrgType = Literal["production", "sandbox", "scratch", "developer", "demo"]
# DomainType = Literal["my", "lightning", "pod"]
# PodType and RegionType can remain if they are not defined in auth.py
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
    r"\.my\.salesforce.com"  # Regular my.salesforce.com
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
    org_type: OrgType = OrgType.PRODUCTION
    if groups.get("org_suffix"):
        org_type = OrgType(groups["org_suffix"])  # type: ignore
    elif groups.get("sandbox_name"):
        org_type = OrgType.SANDBOX

    # Determine domain type
    domain_type: DomainType = DomainType.POD
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

    return SalesforceOrgInfo(
        auth_info=auth_info,
        org_type=org_type,
        domain_type=domain_type,
        full_domain=groups["instance_url"],
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
            if info.domain_type == DomainType.POD:
                print(f"Pod Details:")
                print(f"  Region: {info.region or 'Classic'}")
                print(f"  Number: {info.pod_number or 'N/A'}")
                print(f"  Type: {info.pod_type or 'Standard'}")
                print(f"  Classic: {'Yes' if info.is_classic_pod else 'No'}")
                print(f"  Hyperforce: {'Yes' if info.is_hyperforce else 'No'}")
            else:
                print(f"MyDomain: {info.mydomain}")
                if info.sandbox_name:
                    print(f"Sandbox Name: {info.sandbox_name}")
                print(f"Is Sandbox: {'Yes' if info.is_sandbox else 'No'}")
            print("-" * 30)
        except ValueError as e:
            print(f"Error parsing URL: {e}")


if __name__ == "__main__":
    test_sfdx_auth_url_parser()
