# Integration Points

## Native Integrations

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

- Seamless SFDX/CumulusCI usage
- ITSM system connections
- CI/CD tool bridges
- Deployment frameworks

[Back to Architecture Overview](./index.md)
