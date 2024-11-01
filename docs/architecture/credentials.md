# Credential Management

## Credential Storage

Credential storage is a critical aspect of D2X's security architecture. D2X leverages GitHub's Environments feature to securely store long-lived org credentials (SFDX auth URLs). These credentials are stored in the Base Environment, which implements protection rules and approvals to ensure secure access.

### Key Features

- **Secure Storage**: Long-lived org credentials are securely stored in GitHub Environments.
- **Protection Rules**: Access to credentials is governed by protection rules and approvals.
- **Audit Logs**: All access and operations are logged for auditing purposes.

## Access Management

Access management in D2X is designed to provide temporary, scoped access to credentials. The Session Environment contains temporary access tokens that auto-expire after a configured time. These tokens can be instantly revoked and are scoped to specific jobs and workflows.

### Key Features

- **Temporary Access Tokens**: Access tokens are temporary and auto-expire after a configured time.
- **Scoped Access**: Tokens are scoped to specific jobs and workflows.
- **Instant Revocation**: Tokens can be instantly revoked if needed.

[Back to Architecture Overview](./index.md)
