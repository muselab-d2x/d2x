import unittest
from pydantic import ValidationError
from d2x.models.sf.org import (
    BaseSalesforceOrg,
    ProductionOrg,
    TrialOrg,
    SandboxOrg,
    ScratchOrg,
    OrgType,
    DomainType,
)


class TestBaseSalesforceOrg(unittest.TestCase):
    def test_production_org(self):
        org = ProductionOrg(
            org_type=OrgType.PRODUCTION,
            domain_type=DomainType.POD,
            full_domain="example.salesforce.com",
            instance_url="https://example.salesforce.com",
            created_date="2021-01-01",
            last_modified_date="2021-01-02",
            status="Active",
        )
        self.assertEqual(org.org_type, OrgType.PRODUCTION)
        self.assertEqual(org.domain_type, DomainType.POD)
        self.assertEqual(org.full_domain, "example.salesforce.com")
        self.assertEqual(org.instance_url, "https://example.salesforce.com")
        self.assertEqual(org.created_date, "2021-01-01")
        self.assertEqual(org.last_modified_date, "2021-01-02")
        self.assertEqual(org.status, "Active")

    def test_trial_org(self):
        org = TrialOrg(
            org_type=OrgType.DEMO,
            domain_type=DomainType.POD,
            full_domain="example.salesforce.com",
            instance_url="https://example.salesforce.com",
            created_date="2021-01-01",
            last_modified_date="2021-01-02",
            status="Active",
        )
        self.assertEqual(org.org_type, OrgType.DEMO)
        self.assertEqual(org.domain_type, DomainType.POD)
        self.assertEqual(org.full_domain, "example.salesforce.com")
        self.assertEqual(org.instance_url, "https://example.salesforce.com")
        self.assertEqual(org.created_date, "2021-01-01")
        self.assertEqual(org.last_modified_date, "2021-01-02")
        self.assertEqual(org.status, "Active")

    def test_sandbox_org(self):
        org = SandboxOrg(
            org_type=OrgType.SANDBOX,
            domain_type=DomainType.POD,
            full_domain="example.salesforce.com",
            instance_url="https://example.salesforce.com",
            created_date="2021-01-01",
            last_modified_date="2021-01-02",
            status="Active",
        )
        self.assertEqual(org.org_type, OrgType.SANDBOX)
        self.assertEqual(org.domain_type, DomainType.POD)
        self.assertEqual(org.full_domain, "example.salesforce.com")
        self.assertEqual(org.instance_url, "https://example.salesforce.com")
        self.assertEqual(org.created_date, "2021-01-01")
        self.assertEqual(org.last_modified_date, "2021-01-02")
        self.assertEqual(org.status, "Active")

    def test_scratch_org(self):
        org = ScratchOrg(
            org_type=OrgType.SCRATCH,
            domain_type=DomainType.POD,
            full_domain="example.salesforce.com",
            instance_url="https://example.salesforce.com",
            created_date="2021-01-01",
            last_modified_date="2021-01-02",
            status="Active",
        )
        self.assertEqual(org.org_type, OrgType.SCRATCH)
        self.assertEqual(org.domain_type, DomainType.POD)
        self.assertEqual(org.full_domain, "example.salesforce.com")
        self.assertEqual(org.instance_url, "https://example.salesforce.com")
        self.assertEqual(org.created_date, "2021-01-01")
        self.assertEqual(org.last_modified_date, "2021-01-02")
        self.assertEqual(org.status, "Active")

    def test_invalid_org_type(self):
        with self.assertRaises(ValidationError):
            ProductionOrg(
                org_type="invalid_org_type",
                domain_type=DomainType.POD,
                full_domain="example.salesforce.com",
                instance_url="https://example.salesforce.com",
                created_date="2021-01-01",
                last_modified_date="2021-01-02",
                status="Active",
            )


if __name__ == "__main__":
    unittest.main()
