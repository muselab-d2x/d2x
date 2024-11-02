import json
import unittest
from unittest.mock import patch, MagicMock
from pydantic import SecretStr
from d2x.auth.sf.auth_url import exchange_token, create_scratch_org
from d2x.models.sf.org import SalesforceOrgInfo, ScratchOrg
from d2x.base.types import CLIOptions
from d2x.models.sf.auth import AuthInfo


class TestExchangeToken(unittest.TestCase):
    @patch("d2x.auth.sf.auth_url.set_environment_variable")
    @patch("d2x.auth.sf.auth_url.http.client.HTTPSConnection")
    def test_exchange_token_success(self, mock_https_connection, mock_set_env_var):
        # Mock the SalesforceOrgInfo
        org_info = SalesforceOrgInfo(
            auth_info=AuthInfo(
                client_id="test_client_id",
                client_secret=SecretStr("test_client_secret"),  # Wrapped with SecretStr
                refresh_token="test_refresh_token",
                instance_url="https://test.salesforce.com",
            ),
            org=ScratchOrg(
                org_type="scratch",
                domain_type="my",
                full_domain="test.salesforce.com",
                instance_url="https://test.salesforce.com",
                created_date="2021-01-01",
                last_modified_date="2021-01-02",
                status="Active",
            ),
        )

        # Mock the CLIOptions
        cli_options = CLIOptions(output_format="text", debug=False)

        # Mock the HTTPSConnection and response
        mock_conn = MagicMock()
        mock_https_connection.return_value = mock_conn
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.reason = "OK"
        mock_response.read.return_value = json.dumps(
            {
                "access_token": "test_access_token",
                "instance_url": "https://test.salesforce.com",
                "id": "https://test.salesforce.com/id/00Dxx0000001gEREAY/005xx000001Sv6eAAC",
                "token_type": "Bearer",
                "issued_at": "1627382400000",
                "signature": "test_signature",
            }
        ).encode("utf-8")
        mock_conn.getresponse.return_value = mock_response

        # Call the function
        token_response = exchange_token(org_info, cli_options)

        # Assertions
        self.assertEqual(
            token_response.access_token.get_secret_value(), "test_access_token"
        )
        self.assertEqual(token_response.instance_url, "https://test.salesforce.com")
        mock_set_env_var.assert_called_once_with(
            "salesforce", "ACCESS_TOKEN", "test_access_token"
        )

    @patch("d2x.auth.sf.auth_url.set_environment_variable")
    @patch("d2x.auth.sf.auth_url.http.client.HTTPSConnection")
    def test_exchange_token_failure(self, mock_https_connection, mock_set_env_var):
        # Mock the SalesforceOrgInfo
        org_info = SalesforceOrgInfo(
            auth_info=AuthInfo(
                client_id="test_client_id",
                client_secret=SecretStr("test_client_secret"),  # Wrapped with SecretStr
                refresh_token="test_refresh_token",
                instance_url="https://test.salesforce.com",
            ),
            org=ScratchOrg(
                org_type="scratch",
                domain_type="my",
                full_domain="test.salesforce.com",
                instance_url="https://test.salesforce.com",
                created_date="2021-01-01",
                last_modified_date="2021-01-02",
                status="Active",
            ),
        )

        # Mock the CLIOptions
        cli_options = CLIOptions(output_format="text", debug=False)

        # Mock the HTTPSConnection and response
        mock_conn = MagicMock()
        mock_https_connection.return_value = mock_conn
        mock_response = MagicMock()
        mock_response.status = 400
        mock_response.reason = "Bad Request"
        mock_response.read.return_value = json.dumps(
            {"error": "invalid_grant", "error_description": "authentication failure"}
        ).encode("utf-8")
        mock_conn.getresponse.return_value = mock_response

        # Call the function and assert exception
        with self.assertRaises(RuntimeError):
            exchange_token(org_info, cli_options)


class TestCreateScratchOrg(unittest.TestCase):
    @patch("d2x.auth.sf.auth_url.Salesforce")
    def test_create_scratch_org_success(self, mock_salesforce):
        # Mock the ScratchOrg
        org_info = ScratchOrg(
            org_type="scratch",
            domain_type="my",
            full_domain="test.salesforce.com",
            instance_url="https://test.salesforce.com",
            created_date="2021-01-01",
            last_modified_date="2021-01-02",
            status="Active",
            auth_info=AuthInfo(
                client_id="test_client_id",
                client_secret=SecretStr("test_client_secret"),
                refresh_token="test_refresh_token",
                instance_url="https://test.salesforce.com",
            ),
        )

        # Mock the CLIOptions
        cli_options = CLIOptions(output_format="text", debug=False)

        # Mock the Salesforce instance and response
        mock_sf_instance = MagicMock()
        mock_salesforce.return_value = mock_sf_instance
        mock_sf_instance.restful.return_value = {
            "id": "test_org_id",
            "status": "Active",
            "expirationDate": "2021-01-10",
        }

        # Call the function
        result = create_scratch_org(org_info, cli_options)

        # Assertions
        self.assertEqual(result["id"], "test_org_id")
        self.assertEqual(result["status"], "Active")
        self.assertEqual(result["expirationDate"], "2021-01-10")

    @patch("d2x.auth.sf.auth_url.Salesforce")
    def test_create_scratch_org_failure(self, mock_salesforce):
        # Mock the ScratchOrg
        org_info = ScratchOrg(
            org_type="scratch",
            domain_type="my",
            full_domain="test.salesforce.com",
            instance_url="https://test.salesforce.com",
            created_date="2021-01-01",
            last_modified_date="2021-01-02",
            status="Active",
            auth_info=AuthInfo(
                client_id="test_client_id",
                client_secret=SecretStr("test_client_secret"),
                refresh_token="test_refresh_token",
                instance_url="https://test.salesforce.com",
            ),
        )

        # Mock the CLIOptions
        cli_options = CLIOptions(output_format="text", debug=False)

        # Mock the Salesforce instance and response
        mock_sf_instance = MagicMock()
        mock_salesforce.return_value = mock_sf_instance
        mock_sf_instance.restful.side_effect = Exception("Failed to create scratch org")

        # Call the function and assert exception
        with self.assertRaises(Exception):
            create_scratch_org(org_info, cli_options)


if __name__ == "__main__":
    unittest.main()
