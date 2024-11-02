import unittest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner
from d2x.cli.main import d2x_cli
from d2x.models.sf.org import ScratchOrg
from d2x.models.sf.auth import AuthInfo
from d2x.base.types import CLIOptions


class TestCLICommands(unittest.TestCase):
    @patch("d2x.cli.main.create_scratch_org")
    def test_create_scratch_org_command(self, mock_create_scratch_org):
        runner = CliRunner()
        result = runner.invoke(d2x_cli, ["sf", "org", "create"])

        self.assertEqual(result.exit_code, 0)
        mock_create_scratch_org.assert_called_once()

    @patch("d2x.cli.main.exchange_token")
    def test_exchange_token_command(self, mock_exchange_token):
        runner = CliRunner()
        result = runner.invoke(d2x_cli, ["sf", "org", "exchange"])

        self.assertEqual(result.exit_code, 0)
        mock_exchange_token.assert_called_once()


if __name__ == "__main__":
    unittest.main()
