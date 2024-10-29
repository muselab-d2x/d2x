import os
import unittest
from unittest.mock import patch, MagicMock
from d2x.auth.sf.auth_url import main, exchange_token, parse_sfdx_auth_url
from d2x.auth.sf.models import TokenResponse, SalesforceOrgInfo

class TestAuthUrl(unittest.TestCase):

    @patch("d2x.auth.sf.auth_url.parse_sfdx_auth_url")
    @patch("d2x.auth.sf.auth_url.exchange_token")
    @patch("d2x.auth.sf.auth_url.Console")
    def test_main_success(self, mock_console, mock_exchange_token, mock_parse_sfdx_auth_url):
        # Mock environment variable
        os.environ["SFDX_AUTH_URL"] = "force://PlatformCLI::token123@https://mycompany.my.salesforce.com"

        # Mock parse_sfdx_auth_url return value
        mock_org_info = SalesforceOrgInfo(
            client_id="PlatformCLI",
            client_secret="",
            refresh_token="token123",
            instance_url="https://mycompany.my.salesforce.com",
            org_type="production",
            domain_type="my",
            region=None,
            pod_number=None,
            pod_type=None,
            mydomain="mycompany",
            sandbox_name=None
        )
        mock_parse_sfdx_auth_url.return_value = mock_org_info

        # Mock exchange_token return value
        mock_token_response = TokenResponse(
            access_token="access_token",
            instance_url="https://mycompany.my.salesforce.com",
            issued_at=datetime.now(),
            expires_in=7200,
            token_type="Bearer",
            scope=None,
            signature=None,
            id_token=None
        )
        mock_exchange_token.return_value = mock_token_response

        # Call main function
        with patch("sys.exit") as mock_exit:
            main()
            mock_exit.assert_called_once_with(0)

        # Assertions
        mock_parse_sfdx_auth_url.assert_called_once_with("force://PlatformCLI::token123@https://mycompany.my.salesforce.com")
        mock_exchange_token.assert_called_once_with(mock_org_info, mock_console())

    @patch("d2x.auth.sf.auth_url.parse_sfdx_auth_url")
    @patch("d2x.auth.sf.auth_url.exchange_token")
    @patch("d2x.auth.sf.auth_url.Console")
    def test_main_failure(self, mock_console, mock_exchange_token, mock_parse_sfdx_auth_url):
        # Mock environment variable
        os.environ["SFDX_AUTH_URL"] = "force://PlatformCLI::token123@https://mycompany.my.salesforce.com"

        # Mock parse_sfdx_auth_url to raise an exception
        mock_parse_sfdx_auth_url.side_effect = ValueError("Invalid SFDX auth URL format")

        # Call main function
        with patch("sys.exit") as mock_exit:
            main()
            mock_exit.assert_called_once_with(1)

        # Assertions
        mock_parse_sfdx_auth_url.assert_called_once_with("force://PlatformCLI::token123@https://mycompany.my.salesforce.com")
        mock_exchange_token.assert_not_called()

    @patch("d2x.auth.sf.auth_url.http.client.HTTPSConnection")
    def test_exchange_token_success(self, mock_https_connection):
        # Mock org_info
        mock_org_info = SalesforceOrgInfo(
            client_id="PlatformCLI",
            client_secret="",
            refresh_token="token123",
            instance_url="https://mycompany.my.salesforce.com",
            org_type="production",
            domain_type="my",
            region=None,
            pod_number=None,
            pod_type=None,
            mydomain="mycompany",
            sandbox_name=None
        )

        # Mock HTTPSConnection
        mock_conn = MagicMock()
        mock_https_connection.return_value = mock_conn
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.reason = "OK"
        mock_response.read.return_value = json.dumps({
            "access_token": "access_token",
            "instance_url": "https://mycompany.my.salesforce.com",
            "issued_at": str(int(datetime.now().timestamp() * 1000)),
            "expires_in": 7200,
            "token_type": "Bearer"
        }).encode("utf-8")
        mock_conn.getresponse.return_value = mock_response

        # Call exchange_token function
        console = MagicMock()
        token_response = exchange_token(mock_org_info, console)

        # Assertions
        self.assertEqual(token_response.access_token.get_secret_value(), "access_token")
        self.assertEqual(token_response.instance_url, "https://mycompany.my.salesforce.com")
        self.assertEqual(token_response.expires_in, 7200)
        self.assertEqual(token_response.token_type, "Bearer")

    @patch("d2x.auth.sf.auth_url.http.client.HTTPSConnection")
    def test_exchange_token_failure(self, mock_https_connection):
        # Mock org_info
        mock_org_info = SalesforceOrgInfo(
            client_id="PlatformCLI",
            client_secret="",
            refresh_token="token123",
            instance_url="https://mycompany.my.salesforce.com",
            org_type="production",
            domain_type="my",
            region=None,
            pod_number=None,
            pod_type=None,
            mydomain="mycompany",
            sandbox_name=None
        )

        # Mock HTTPSConnection
        mock_conn = MagicMock()
        mock_https_connection.return_value = mock_conn
        mock_response = MagicMock()
        mock_response.status = 400
        mock_response.reason = "Bad Request"
        mock_response.read.return_value = json.dumps({
            "error": "invalid_grant",
            "error_description": "authentication failure"
        }).encode("utf-8")
        mock_conn.getresponse.return_value = mock_response

        # Call exchange_token function
        console = MagicMock()
        with self.assertRaises(RuntimeError):
            exchange_token(mock_org_info, console)

        # Assertions
        mock_conn.request.assert_called_once()
        mock_conn.getresponse.assert_called_once()

if __name__ == "__main__":
    unittest.main()
