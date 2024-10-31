# 🏗️ D2X Technical Architecture

## Core Design Principles

D2X minimizes complexity by leveraging GitHub's platform features rather than building parallel systems. This approach:

-   Makes enterprise features accessible to everyone
-   Reduces security attack surface
-   Enables native integration with GitHub's ecosystem
-   Simplifies maintenance and updates

## 🔐 Environment Structure

The foundation of D2X's security model is GitHub's Environments feature, used in a novel two-stage pattern:

```mermaid
stateDiagram-v2
    [*] --> BaseEnvironment
    state BaseEnvironment {
        [*] --> StoreCredential
        StoreCredential --> ProtectAccess
        ProtectAccess --> WaitForRequest
        WaitForRequest --> ExchangeToken
    }

    state SessionEnvironment {
        [*] --> CreateTemporary
        CreateTemporary --> SetTimeLimit
        SetTimeLimit --> GrantAccess
        GrantAccess --> MonitorUsage
        MonitorUsage --> Revoke
    }

    BaseEnvironment --> SessionEnvironment: Token Exchange
    SessionEnvironment --> [*]: Auto Expire/Revoke
```

### Base Environment

-   Stores long-lived org credentials (SFDX auth URLs)
-   Implements protection rules and approvals
-   Handles token exchange requests
-   Maintains audit logs

### Session Environment

-   Contains temporary access tokens
-   Auto-expires after configured time
-   Can be instantly revoked
-   Scoped to specific jobs/workflows

[Learn more about environment configuration](./architecture/environments.md)

## 📦 Repository Architecture

D2X uses GitHub's repository features to represent Salesforce orgs and their relationships:

```mermaid
flowchart TB
    subgraph "Repository Structure"
        direction TB
        BaseRepo["Base Repository Template"]
        OrgRepo["Org-Specific Repository"]
        TeamFork["Team Fork"]

        subgraph "Repository Components"
            Config["cumulusci.yml"]
            Workflows[".github/workflows"]
            Source["force-app/"]
            Scripts["scripts/"]
        end

        subgraph "Branch Protection"
            Reviews["Required Reviews"]
            Checks["Status Checks"]
            Scans["Security Scans"]
        end

        BaseRepo -->|"Create"| OrgRepo
        OrgRepo -->|"Fork"| TeamFork
        TeamFork -->|"PR"| OrgRepo

        Config --> Checks
        Workflows --> Checks
        Scans -->|"Gate"| Reviews
    end
```

### Repository Types

-   Base templates for different org patterns
-   Org-specific repositories (forked from templates)
-   Team forks for development

### Security Features

-   Branch protection rules
-   Required status checks
-   Automated security scanning
-   Pull request reviews

[Learn more about repository features](./architecture/repositories.md)

## ⚡ Actions & Workflows

D2X provides reusable workflows that leverage GitHub Actions:

```mermaid
flowchart TB
    subgraph "Workflow Components"
        subgraph "Security Layer"
            Auth["Authentication"]
            Session["Session Management"]
            Secrets["Secret Handling"]
        end

        subgraph "Core Operations"
            Deploy["Deployment"]
            Test["Testing"]
            Validate["Validation"]
        end

        subgraph "Integration Layer"
            SFDX["SFDX Bridge"]
            CCI["CumulusCI Bridge"]
            External["External Services"]
        end

        Auth --> Session
        Session --> Core["Core Operations"]
        Core --> Integration["Integration Layer"]
    end
```

### Composable Design

Each workflow is built from smaller, reusable components that can be:

-   Combined in different ways
-   Customized as needed
-   Versioned independently
-   Shared across repositories

[Learn more about workflow patterns](./architecture/workflows.md)

## 🔌 Integration Points

D2X bridges GitHub with your existing tools and processes:

```mermaid
flowchart LR
    subgraph "GitHub Platform"
        Actions["GitHub Actions"]
        Environments["Environments"]
        Secrets["Secrets"]
    end

    subgraph "Development Tools"
        SFDX["SFDX"]
        CCI["CumulusCI"]
        VS["VS Code"]
    end

    subgraph "External Systems"
        ITSM["ITSM Tools"]
        CI["CI Systems"]
        Deploy["Deployment Tools"]
    end

    GitHub --> Development
    GitHub --> External
```

### Native Integrations

-   Seamless SFDX/CumulusCI usage
-   ITSM system connections
-   CI/CD tool bridges
-   Deployment frameworks

[Learn more about integrations](./architecture/integrations.md)
