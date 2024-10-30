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

## D2X `cumulusci-next`

Learn more about advance features of CumulusCI contained in Muselab's preview `cumulusci-next` branch of `d2x` and the corresponding Docker image tag to try out new features like Scratch Org Snapshot management, additional yaml loadable from the command line, a simple plugin framework, and more.

Check out [D2X cumulusci-next](cumulusci-next.md) for more details.

## Vision for D2X

D2X is designed to be the future of Salesforce DevOps, providing a scalable, secure, and highly productive framework for managing multiple Salesforce customer org configurations. The vision for D2X includes:

- **Scalability**: D2X supports a growing customer base through automation, reducing manual effort and increasing efficiency.
- **Security**: Implements GitHub Advanced Security scanning and proper secret management to eliminate exposed credentials.
- **Cost Reduction**: Reduces per-release effort significantly, providing a high return on investment.
- **Compliance**: Enables audit trails and standardized processes, ensuring compliance with industry standards.
- **Quality**: Reduces deployment errors through automation, improving overall quality and customer satisfaction.

For more details on the architecture, implementation priorities, ROI analysis, and next steps, refer to the [Vision for D2X](vision.md) document.

For a hypothetical case study showing the projected benefits of the d2x vision, refer to the [Vision OEM](vision-oem.md) document.

## Troubleshooting

Need help troubleshooting an error? Check out the [Troubleshooting](troubleshooting.md) section for common error messages and tips on debugging issues.

## Resources

D2X itself doesn't require a lot of documentation. It's really about stitching together some amazingly powerful tools. Learning those tools is an important part of learning to work with D2X. The following documentation provides resouces to learn about those tools:

-   [CumulusCI Documentation](https://cumulusci.readthedocs.io)
-   [Trailhead: Build Applications with CumulusCI](https://trailhead.salesforce.com/content/learn/trails/build-applications-with-cumulusci)
-   [Salesforce CLI](https://developer.salesforce.com/tools/salesforcecli)
