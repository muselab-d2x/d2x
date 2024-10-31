import unittest
from unittest.mock import patch
from d2x.auth.sf.login_url import generate_login_url, main as login_url_main
from d2x.models.sf.org import SalesforceOrgInfo
from d2x.base.types import CLIOptions
from d2x.models.sf.auth import AuthInfo


class TestGenerateLoginUrl(unittest.TestCase):
    @patch("d2x.auth.sf.login_url.get_environment_variable")
    def test_generate_login_url_success(self, mock_get_env_var):
        # Mock the SalesforceOrgInfo
        org_info = SalesforceOrgInfo(
            auth_info=AuthInfo(
                client_id="test_client_id",
                client_secret="test_client_secret",
                refresh_token="test_refresh_token",
                instance_url="https://test.salesforce.com",
            ),
            org_type="production",
            domain_type="pod",
            full_domain="test.salesforce.com",
        )

        # Mock the CLIOptions
        cli_options = CLIOptions(output_format="text", debug=False)

        # Mock the get_environment_variable function
        mock_get_env_var.return_value = "test_access_token"

        # Call the function
        login_url = generate_login_url(
            instance_url=org_info.auth_info.instance_url,
            access_token="test_access_token",
        )

        # Assertions
        self.assertIn("https://test.salesforce.com", login_url)
        self.assertIn("test_access_token", login_url)

    @patch("d2x.auth.sf.login_url.get_environment_variable")
    def test_generate_login_url_failure(self, mock_get_env_var):
        # Mock the SalesforceOrgInfo
        org_info = SalesforceOrgInfo(
            auth_info=AuthInfo(
                client_id="test_client_id",
                client_secret="test_client_secret",
                refresh_token="test_refresh_token",
                instance_url="https://test.salesforce.com",
            ),
            org_type="production",
            domain_type="pod",
            full_domain="test.salesforce.com",
        )

        # Mock the CLIOptions
        cli_options = CLIOptions(output_format="text", debug=False)

        # Mock the get_environment_variable function to raise an exception
        mock_get_env_var.side_effect = Exception("Error retrieving access token")

        # Call the function and assert exception
        with self.assertRaises(Exception):
            login_url_main(cli_options)


if __name__ == "__main__":
    unittest.main()
