import unittest
from unittest.mock import patch, MagicMock
from d2x.api.sf.metadata.tracking import (
    get_valid_target_directories,
    run_retrieve_task,
    commit_changes_to_github,
    get_salesforce_connection,
    get_latest_revision_numbers,
    compare_revisions,
)


class TestMetadataTracking(unittest.TestCase):
    @patch("d2x.api.sf.metadata.tracking.get_repo_info")
    @patch("d2x.api.sf.metadata.tracking.get_source_format")
    @patch("d2x.api.sf.metadata.tracking.os.path.isdir")
    @patch("d2x.api.sf.metadata.tracking.os.listdir")
    @patch("builtins.open", new_callable=unittest.mock.mock_open, read_data='{"packageDirectories": [{"path": "force-app", "default": True}]}')
    def test_get_valid_target_directories(self, mock_open, mock_listdir, mock_isdir, mock_get_source_format, mock_get_repo_info):
        mock_get_repo_info.return_value = MagicMock()
        mock_get_source_format.return_value = "sfdx"
        mock_isdir.side_effect = lambda x: x in ["unpackaged/pre", "unpackaged/post", "unpackaged/config"]
        mock_listdir.side_effect = lambda x: ["dir1", "dir2"]

        user = MagicMock()
        scratch_org = MagicMock()
        repo_root = "repo_root"

        package_directories, sfdx = get_valid_target_directories(user, scratch_org, repo_root)

        self.assertEqual(package_directories["source"], ["force-app"])
        self.assertEqual(package_directories["pre"], ["unpackaged/pre/dir1", "unpackaged/pre/dir2"])
        self.assertEqual(package_directories["post"], ["unpackaged/post/dir1", "unpackaged/post/dir2"])
        self.assertEqual(package_directories["config"], ["unpackaged/config/dir1", "unpackaged/config/dir2"])
        self.assertTrue(sfdx)

    @patch("d2x.api.sf.metadata.tracking.refresh_access_token")
    @patch("d2x.api.sf.metadata.tracking.get_repo_info")
    @patch("d2x.api.sf.metadata.tracking.BaseCumulusCI")
    @patch("d2x.api.sf.metadata.tracking.get_valid_target_directories")
    @patch("d2x.api.sf.metadata.tracking.retrieve_components")
    def test_run_retrieve_task(self, mock_retrieve_components, mock_get_valid_target_directories, mock_BaseCumulusCI, mock_get_repo_info, mock_refresh_access_token):
        mock_get_repo_info.return_value = MagicMock()
        mock_refresh_access_token.return_value = MagicMock()
        mock_BaseCumulusCI.return_value = MagicMock()
        mock_get_valid_target_directories.return_value = ({"source": ["force-app"]}, True)

        user = MagicMock()
        scratch_org = MagicMock()
        project_path = "project_path"
        desired_changes = {"ApexClass": ["TestClass"]}
        target_directory = "force-app"
        originating_user_id = "user_id"

        run_retrieve_task(user, scratch_org, project_path, desired_changes, target_directory, originating_user_id)

        mock_retrieve_components.assert_called_once()

    @patch("d2x.api.sf.metadata.tracking.local_github_checkout")
    @patch("d2x.api.sf.metadata.tracking.run_retrieve_task")
    @patch("d2x.api.sf.metadata.tracking.get_repo_info")
    @patch("d2x.api.sf.metadata.tracking.CommitDir")
    def test_commit_changes_to_github(self, mock_CommitDir, mock_get_repo_info, mock_run_retrieve_task, mock_local_github_checkout):
        mock_local_github_checkout.return_value.__enter__.return_value = "project_path"
        mock_get_repo_info.return_value = MagicMock()
        mock_run_retrieve_task.return_value = None
        mock_CommitDir.return_value = MagicMock()

        user = MagicMock()
        scratch_org = MagicMock()
        repo_id = "repo_id"
        branch = "branch"
        desired_changes = {"ApexClass": ["TestClass"]}
        commit_message = "commit_message"
        target_directory = "force-app"
        originating_user_id = "user_id"

        commit_changes_to_github(user, scratch_org, repo_id, branch, desired_changes, commit_message, target_directory, originating_user_id)

        mock_run_retrieve_task.assert_called_once()
        mock_CommitDir.assert_called_once()

    @patch("d2x.api.sf.metadata.tracking.refresh_access_token")
    @patch("d2x.api.sf.metadata.tracking.simple_salesforce.Salesforce")
    def test_get_salesforce_connection(self, mock_Salesforce, mock_refresh_access_token):
        mock_refresh_access_token.return_value = MagicMock()
        mock_Salesforce.return_value = MagicMock()

        scratch_org = MagicMock()
        originating_user_id = "user_id"
        base_url = "base_url"

        conn = get_salesforce_connection(scratch_org=scratch_org, originating_user_id=originating_user_id, base_url=base_url)

        self.assertIsNotNone(conn)
        mock_Salesforce.assert_called_once()

    @patch("d2x.api.sf.metadata.tracking.get_salesforce_connection")
    def test_get_latest_revision_numbers(self, mock_get_salesforce_connection):
        mock_conn = MagicMock()
        mock_conn.query_all.return_value = {
            "records": [
                {"MemberName": "TestClass", "MemberType": "ApexClass", "RevisionCounter": 1}
            ]
        }
        mock_get_salesforce_connection.return_value = mock_conn

        scratch_org = MagicMock()
        originating_user_id = "user_id"

        revisions = get_latest_revision_numbers(scratch_org, originating_user_id=originating_user_id)

        self.assertEqual(revisions, {"ApexClass": {"TestClass": 1}})

    def test_compare_revisions(self):
        old_revision = {"ApexClass": {"TestClass": 1}}
        new_revision = {"ApexClass": {"TestClass": 2}}

        changes = compare_revisions(old_revision, new_revision)

        self.assertEqual(changes, {"ApexClass": ["TestClass"]})


if __name__ == "__main__":
    unittest.main()
