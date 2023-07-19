# Welcome to MuseLab D2X

MuseLab D2X is an open source collection of processes and tools that make it easy implement and operate a comprehensive Development to Delivery Experience (D2X) for reusable and composable Salesforce products and services.

D2X combines the best of CumulusCI, Salesforce CLI, GitHub Actions, and GitHub Codespaces.

All D2X projects start off with batteries included such as:

* CumulusCI & Salesforce DX project configuration
* GitHub Actions CI/CD Builds
  * Feature Test
  * Beta Release/Test
  * Production Release
* Pre-configured Devcontainer ready to use with GitHub Codespaces or the VS Code Devcontainers extension to provide a consistent, fully configured runtime environments to everyone working on the project and build 
* Reduced maintainance via the ghcr.io/muselab-d2x/d2x:latest Docker image used throughout the lifecycle and maintained by MuseLab

## Starting a D2X Project

The easiest way to get started is with the D2X Launchpad application which provides a simple web interface to launching new GitHub repositories fully configured for D2X:
[https://launchpad.muselab.com]

### Using with an existing GitHub repository
TBD

## Using a D2X Project

D2X provides a consistent developer experience across all D2X projects.

### Launching a development environment

We recommend using GitHub Codespaces as development environments for greater productivity, reduced developer tooling support burden, and security. Codespaces provides on-demand, web based VS Code instances. D2X provides a customized Codespaces image that includes all the right tooling versions and configurations.

To launch a Codespace, simply click Code then select the Codespaces tab on the GitHub repository's main page.

#### Setting up DEV_HUB_AUTH_URL

Your Codespaces need access to your DevHub to create scratch orgs. You can configure the DEV_HUB_AUTH_URL secret on your GitHub account to provide all your Codespaces with access to the DevHub automatically. This is a one-time setup operation for all your Codespaces.

To start, you need to get the sfdxAuthUrl for your DevHub. To do this, you can use sfdx either on your computer or via Codespaces.

** via Codespaces **
If you don't already have sfdx installed on your computer and connected to your DevHub, you can use a Codespace to connect to the DevHub so you can get the sfdxAuthUrl. Simply launch a new Codespace from your D2X project repository then run:
`sfdx org login device --set-default-dev-hub --alias DevHub`

** via sfdx **
Assuming you already have sfdx installed on your computer and connected to your DevHub as the alias `DevHub`, you should be able to get the Sfdx Auth Url (starts with force://) by running `sfdx org display -o DevHub --verbose` andy copying the auth url (starts with force://, ends with .salesforce.com)