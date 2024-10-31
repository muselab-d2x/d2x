# Environment Configuration

## Base Environment

The Base Environment is responsible for storing long-lived org credentials (SFDX auth URLs) and implementing protection rules and approvals. It handles token exchange requests and maintains audit logs.

## Session Environment

The Session Environment contains temporary access tokens that auto-expire after a configured time. It can be instantly revoked and is scoped to specific jobs/workflows.

[Back to Architecture Overview](./index.md)
