D2X lets teams deliver repeatable, composable Salesforce products and solutions that align with Salesforce's [Well-Architected Framework](https://architect.salesforce.com/well-architected/overview).

D2X defines a container image for Salesforce development, build, and delivery using CumulusCI and Salesforce CLI. This gives teams a cconsistent runtime environment for automation used in across the entire software product lifecycle.

MuseLab created D2X as the framework for all of our [services engagements](https://muselab.com/services), and we are proud to share it freely with the entire Salesforce ecosystem.

See [D2X documentation](https://d2x.readthedocs.io) for more details on using D2X — or try it yourself right now via [D2X Launchpad](https://launchpad.muselab.com)! 

Stay tuned for details on how to contribute!

## New Workflow: delete-environment.yml

A new reusable workflow `delete-environment.yml` has been added to delete an environment and revoke the Salesforce token. This workflow includes steps to authenticate to DevHub, delete the environment, and revoke the Salesforce token using new d2x commands.

### Usage Instructions

To use the `delete-environment.yml` workflow, follow these steps:

1. Create a new workflow file in your repository (e.g., `.github/workflows/delete-environment.yml`).
2. Copy the following content into the new workflow file:

```yaml
name: Delete Environment

on:
  workflow_call:
    inputs:
      env-name:
        required: true
        type: string
      sf-auth-url:
        required: true
        type: string
    secrets:
      dev-hub-auth-url:
        required: true
      github-token:
        required: true

jobs:
  delete-environment:
    name: "Delete Environment"
    runs-on: ubuntu-latest
    container:
      image: ghcr.io/muselab-d2x/d2x:cumulusci-next
      options: --user root
      credentials:
        username: ${{ github.actor }}
        password: ${{ secrets.github-token }}
      env:
        DEV_HUB_AUTH_URL: "${{ secrets.dev-hub-auth-url }}"
        CUMULUSCI_SERVICE_github: '{ "username": "${{ github.actor }}", "token": "${{ secrets.github-token }}", "email": "NOTUSED" }'
    steps:
      - name: Checkout
        uses: actions/checkout@v2

      - name: Auth to DevHub
        run: /usr/local/bin/devhub.sh

      - name: Delete Environment
        run: cci org scratch_delete ${{ inputs.env-name }}
        shell: bash

      - name: Revoke Salesforce Token
        run: |
          python -c "
import os
from d2x.auth.sf.auth_url import revoke_sf_token
from rich.console import Console

console = Console()
sf_auth_url = os.environ.get('SF_AUTH_URL')
access_token = os.environ.get('ACCESS_TOKEN')
instance_url = os.environ.get('INSTANCE_URL')

revoke_sf_token(instance_url, access_token, console)
"
        env:
          SF_AUTH_URL: ${{ inputs.sf-auth-url }}
          ACCESS_TOKEN: ${{ steps.auth_to_devhub.outputs.access_token }}
          INSTANCE_URL: ${{ steps.auth_to_devhub.outputs.instance_url }}
```

3. Customize the workflow inputs and secrets as needed for your environment.

## New Command: revoke_sf_token

A new command `revoke_sf_token` has been added to the `d2x` library to handle token revocation by making appropriate API calls to Salesforce.

### Usage Instructions

To use the `revoke_sf_token` command, follow these steps:

1. Import the `revoke_sf_token` function from the `d2x.auth.sf.auth_url` module:

```python
from d2x.auth.sf.auth_url import revoke_sf_token
```

2. Call the `revoke_sf_token` function with the required parameters:

```python
from rich.console import Console

console = Console()
instance_url = "https://your-instance.salesforce.com"
access_token = "your-access-token"

revoke_sf_token(instance_url, access_token, console)
```

The `revoke_sf_token` function will make an API call to Salesforce to revoke the specified token and display the result in the console.
