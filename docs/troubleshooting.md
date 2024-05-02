# Troubleshooting D2X

## Common Errors

### GitHub Actions

#### Error: The template is not valid. muselab-d2x/d2x/.github/workflows/feature-test-unlocked.yml@main (Line: 35, Col: 27): Unexpected value ''

This error can occur when you have a project that uses dependencies and you haven't set up the `CCI_GITHUB_TOKEN` secret for the repository in GitHub or haven't granted the repository permission to an organization level secret. Ensure that the `CCI_GITHUB_TOKEN` secret is available in the repository under Settings -> Secrets and variables -> Actions.

#### _In Set Commit Status Step_ gh: Not Found (HTTP 404)

Check that the GitHub Personal Access Token being used for the `CCI_GITHUB_TOKEN` secret has access to the repository being built.
