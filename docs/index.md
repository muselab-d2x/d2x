# Introducing D2X

D2X is an open source collection of tools and configurations to quickly launch and easily maintain Salesforce development projects on GitHub. D2X combines the best of CumulusCI, Salesforce CLI, GitHub Actions, and GitHub Codespaces. D2X projects are set up to align with the Salesforce Well-Architected principle of [Adaptable (Resilient and Composable)](https://architect.salesforce.com/well-architected/adaptable/overview).

D2X is made up of:

-   A Docker image with the latest versions of CumulusCI and SF CLI preinstalled

    -   GitHub Package: https://github.com/muselab-d2x/d2x/pkgs/container/d2x
    -   Latest Docker Image: `ghcr.io/muselab-d2x/d2x:latest`

-   A set of [reusable GitHub Actions workflows](https://github.com/muselab-d2x/d2x/tree/main/.github/workflows)
-   A [devcontainer](https://containers.dev) [configuration](https://github.com/muselab-d2x/d2x/tree/main/.devcontainer) for use with GitHub Codespaces or any IDE with a Devcontainers extension
-   A [project template](https://github.com/muselab-d2x/d2x-template) using [cookiecutter](https://cookiecutter.readthedocs.io)

D2X is a project of [MuseLab](https://muselab.com) and was created to support our [consulting services](https://muselab.com/services) with Salesforce partners and customers. We proudly share D2X as open source with the Salesforce community as part of our goal to revolutionize and democratize Salesforce DevOps.

## Starting a D2X Project

The easiest way to get started is with [D2X Launchpad](https://launchpad.muselab.com) which provides a simple web interface to launching new GitHub repositories fully configured for D2X.

## Post-Launch Tutorial

You've created your own GitHub repository using [D2X Launchpad](https://launchpad.muselab.com), now what?

Head over to the [D2X Project Tutorial](tutorial.md) for next steps on finalizing your project's setup and getting started building.

## Troubleshooting

Need help troubleshooting an error? Check out the [Troubleshooting](troubleshooting.md) section for common error messages and tips on debugging issues.

## Resources

D2X itself doesn't require a lot of documentation. It's really about stitching together some amazingly powerful tools. Learning those tools is an important part of learning to work with D2X. The following documentation provides resouces to learn about those tools:

-   [CumulusCI Documentation](https://cumulusci.readthedocs.io)
-   [Trailhead: Build Applications with CumulusCI](https://trailhead.salesforce.com/content/learn/trails/build-applications-with-cumulusci)
-   [Salesforce CLI](https://developer.salesforce.com/tools/salesforcecli)
