# 🛡️ Security Workflows

## Two-Stage Authentication

Two-stage authentication is a process that separates long-term credentials from temporary access tokens to enhance security.

### Steps

1. **Request Access**: The GitHub job requests access from the base environment.
2. **Exchange Token**: The base environment exchanges the token with Salesforce.
3. **Store Token**: The session environment stores the token.
4. **Provide Access**: The session environment provides access to the GitHub job.
5. **Auto-Expire**: The token auto-expires after a configured time.
6. **Revoke Access**: The session environment revokes access.

### Diagram

```mermaid
sequenceDiagram
    participant Job as GitHub Job
    participant Base as Base Environment
    participant Session as Session Environment
    participant SF as Salesforce

    Job->>Base: Request Access
    Base->>SF: Exchange Token
    SF-->>Base: Access Token
    Base->>Session: Store Token
    Session-->>Job: Provide Access
    Note over Session: Token Auto-Expires
    Session->>Job: Revoke Access
```

## Protected Deployments

Protected deployments ensure that deployments to production environments are secure and compliant with approval processes.

### Steps

1. **Request Deploy**: The developer requests a deployment.
2. **Check Protection Rules**: GitHub checks the protection rules in the environment.
3. **Request Approvals**: If required, GitHub requests approvals.
4. **Wait for Approvers**: GitHub waits for the necessary approvals.
5. **Execute Deploy**: GitHub executes the deployment to Salesforce.
6. **Deployment Results**: Salesforce returns the deployment results to GitHub.

### Diagram

```mermaid
sequenceDiagram
    participant Dev as Developer
    participant GH as GitHub
    participant Env as Environment
    participant SF as Salesforce

    Dev->>GH: Request Deploy
    GH->>Env: Check Protection Rules
    alt Requires Approval
        Env->>GH: Request Approvals
        Note over GH: Wait for Approvers
    end
    GH->>SF: Execute Deploy
    SF-->>GH: Results
```

[Back to Workflow Overview](./index.md)
