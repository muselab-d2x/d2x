# Customer Org Management Architecture

## Executive Summary

This architecture addresses critical business challenges in managing multiple Salesforce customer org configurations, offering significant ROI through:

- **Cost Reduction**: Reduces per-release effort from 320 hours (80 customers × 4 hours) to ~8-16 hours of oversight
- **Risk Mitigation**: Eliminates exposed credentials through centralized secrets management
- **Scalability**: Supports growing customer base through automation
- **Security**: Implements GitHub Advanced Security scanning and proper secret management
- **Compliance**: Enables audit trails and standardized processes

## 1. Repository Architecture

### a. Base Customer Org Repository

Purpose:
- Acts as the template repository containing the base configuration for customer orgs
- Includes common CumulusCI configurations, scripts, and workflows

Features:
- Branch Structure:
  - Use branches to represent different versions or environments (e.g., main, develop, release)
- GitHub Features:
  - Enable issues, wikis, and projects for documentation and tracking

For more details, refer to the [Base Customer Org Repository](vision-oem.md#base-customer-org-repository) section in the Vision OEM document.

### b. Per-Customer Repositories

Forking Strategy:
- Each customer gets a repository that is a fork of the base customer org repository
- This allows you to push updates to the base repo and have customers merge changes into their forks

Benefits:
- Inheritance of Changes:
  - Easy propagation of updates from the base repo to customer repos
- Customization:
  - Customers can have specific configurations or overrides in their repositories

Management:
- Naming Conventions:
  - Use consistent naming for customer repos (e.g., customer-<CustomerName>)
- Access Control:
  - Restrict access to customer repositories to authorized personnel only

For more details, refer to the [Per-Customer Repositories](vision-oem.md#per-customer-repositories) section in the Vision OEM document.

### c. Forks and Collaboration

Additional Forks:
- Developers or team members can fork customer repositories as needed for development or testing
- Pull requests can be used to merge changes back into the customer repo

For more details, refer to the [Forks and Collaboration](vision-oem.md#forks-and-collaboration) section in the Vision OEM document.

## 2. Secrets and Secure Configuration Management

### a. GitHub Secrets

Per-Repository Secrets:
- Store customer-specific secrets (e.g., Salesforce credentials, API keys) in the customer repository's Secrets
- GitHub encrypts these secrets and makes them available to workflows

Security Considerations:
- Least Privilege:
  - Only store secrets necessary for that customer
- Rotation Policies:
  - Implement regular secret rotation to enhance security

For more details, refer to the [GitHub Secrets](vision-oem.md#github-secrets) section in the Vision OEM document.

### b. GitHub Environments

Purpose:
- Environments in GitHub can be used to define variables and secrets that are environment-specific (e.g., staging, production)

Features:
- Protection Rules:
  - Require approvals before workflows can run against certain environments
- Environment Secrets:
  - Override repository-level secrets for specific environments

For more details, refer to the [GitHub Environments](vision-oem.md#github-environments) section in the Vision OEM document.

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600">
  <!-- Repository Architecture -->
  <rect x="50" y="50" width="200" height="150" fill="#e3f2fd" stroke="#1565c0" stroke-width="2"/>
  <text x="150" y="85" text-anchor="middle" font-family="Arial" font-size="14" fill="#1565c0" font-weight="bold">Base Repository</text>
  
  <rect x="70" y="100" width="160" height="80" fill="#fff" stroke="#1565c0" stroke-width="1"/>
  <text x="150" y="130" text-anchor="middle" font-family="Arial" font-size="12">cumulusci.yml</text>
  <text x="150" y="150" text-anchor="middle" font-family="Arial" font-size="12">GitHub Actions</text>
  <text x="150" y="170" text-anchor="middle" font-family="Arial" font-size="12">Scripts</text>

  <!-- Customer Repos -->
  <rect x="400" y="50" width="180" height="120" fill="#f3e5f5" stroke="#7b1fa2" stroke-width="2"/>
  <text x="490" y="85" text-anchor="middle" font-family="Arial" font-size="14" fill="#7b1fa2">Customer A Repo</text>
  
  <rect x="400" y="200" width="180" height="120" fill="#f3e5f5" stroke="#7b1fa2" stroke-width="2"/>
  <text x="490" y="235" text-anchor="middle" font-family="Arial" font-size="14" fill="#7b1fa2">Customer B Repo</text>

  <!-- Arrows -->
  <path d="M 250 125 L 400 110" fill="none" stroke="#1565c0" stroke-width="2" marker-end="url(#arrow)"/>
  <path d="M 250 125 L 400 260" fill="none" stroke="#1565c0" stroke-width="2" marker-end="url(#arrow)"/>

  <!-- Arrow Marker -->
  <defs>
    <marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="5" orient="auto">
      <path d="M0,0 L10,5 L0,10" fill="none" stroke="#1565c0"/>
    </marker>
  </defs>

  <!-- Legend -->
  <rect x="50" y="500" width="700" height="80" fill="#fafafa" stroke="#616161" stroke-width="1"/>
  <text x="70" y="530" font-family="Arial" font-size="12" fill="#616161">Base Repository: Contains template configurations</text>
  <text x="70" y="550" font-family="Arial" font-size="12" fill="#616161">Customer Repositories: Forked from base, contain customer-specific settings</text>
  <text x="70" y="570" font-family="Arial" font-size="12" fill="#616161">Arrows: Represent inheritance and update flow</text>
</svg>

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 400">
  <!-- Deployment Flow -->
  <rect x="50" y="50" width="700" height="300" fill="#f5f5f5" stroke="#424242" stroke-width="2"/>
  <text x="400" y="90" text-anchor="middle" font-family="Arial" font-size="16" fill="#424242" font-weight="bold">Deployment Workflow</text>

  <!-- Flow Steps -->
  <circle cx="150" cy="200" r="40" fill="#c8e6c9" stroke="#2e7d32" stroke-width="2"/>
  <text x="150" y="205" text-anchor="middle" font-family="Arial" font-size="12">Start</text>

  <circle cx="300" cy="200" r="40" fill="#bbdefb" stroke="#1565c0" stroke-width="2"/>
  <text x="300" y="195" text-anchor="middle" font-family="Arial" font-size="12">Security</text>
  <text x="300" y="210" text-anchor="middle" font-family="Arial" font-size="12">Scan</text>

  <circle cx="450" cy="200" r="40" fill="#bbdefb" stroke="#1565c0" stroke-width="2"/>
  <text x="450" y="195" text-anchor="middle" font-family="Arial" font-size="12">Build &</text>
  <text x="450" y="210" text-anchor="middle" font-family="Arial" font-size="12">Validate</text>

  <circle cx="600" cy="200" r="40" fill="#c8e6c9" stroke="#2e7d32" stroke-width="2"/>
  <text x="600" y="205" text-anchor="middle" font-family="Arial" font-size="12">Deploy</text>

  <!-- Connecting Lines -->
  <line x1="190" y1="200" x2="260" y2="200" stroke="#424242" stroke-width="2" marker-end="url(#arrow2)"/>
  <line x1="340" y1="200" x2="410" y2="200" stroke="#424242" stroke-width="2" marker-end="url(#arrow2)"/>
  <line x1="490" y1="200" x2="560" y2="200" stroke="#424242" stroke-width="2" marker-end="url(#arrow2)"/>

  <!-- Arrow Marker -->
  <defs>
    <marker id="arrow2" markerWidth="10" markerHeight="10" refX="9" refY="5" orient="auto">
      <path d="M0,0 L10,5 L0,10" fill="none" stroke="#424242"/>
    </marker>
  </defs>
</svg>
