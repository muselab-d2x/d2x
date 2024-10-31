# ⚙️ GitHub Platform Features

D2X leverages GitHub's platform features in novel ways to create a secure, scalable DevOps solution:

## 🏗️ Core Platform Features

### Environments

GitHub Environments become a secure credential vault and access management system:

```mermaid
flowchart TB
    subgraph "GitHub Environments"
        Base["Base Environment<br/>Long-term Credentials"]
        Session["Session Environment<br/>Temporary Access"]
        Protection["Protection Rules<br/>Access Controls"]

        Base -->|"Token Exchange"| Session
        Protection -->|"Gates"| Session
    end
```

### Actions

Reusable workflows enable composable automation while maintaining security:

```mermaid
flowchart LR
    subgraph "GitHub Actions"
        Reusable["Reusable Workflows"]
        Composite["Composite Actions"]
        Security["Security Checks"]

        Reusable -->|"Compose"| Composite
        Security -->|"Gate"| Composite
    end
```

### Advanced Security

Native security features protect your entire pipeline:

-   Secret scanning
-   Code scanning
-   Dependency analysis
-   Security policies

### Repository Features

From wikis to projects, every feature serves a purpose:

-   Branch protection
-   Status checks
-   Automated reviews
-   Documentation

[Learn more about GitHub features](./features/index.md)

# 🤝 Community

## Open Source at Heart

D2X is built in the open, leveraging GitHub's collaboration features to create a vibrant ecosystem where everyone benefits.

```mermaid
flowchart TB
    subgraph "Community Ecosystem"
        Core["Core Project"]
        Extensions["Extensions"]
        Templates["Templates"]
        Docs["Documentation"]

        Core -->|"Inspire"| Extensions
        Core -->|"Share"| Templates
        Community -->|"Contribute"| Core
        Community -->|"Improve"| Docs
    end
```

## Ways to Contribute

-   💡 Share ideas in Discussions
-   🐛 Report issues
-   🔀 Submit pull requests
-   📚 Improve documentation

## Getting Help

-   📖 Documentation
-   💬 Community discussions
-   🎓 Learning resources
-   👥 User groups

[Join the community on GitHub](https://github.com/muselab-d2x/d2x/discussions)

## Looking Forward

Together, we're building a future where secure, scalable Salesforce DevOps is accessible to everyone. Whether you're managing a single org or hundreds, your experience and ideas can help shape this future.
