# D2X cumulusci-next

## Overview

D2X [muselab-d2x/d2x@cumulusci-next](https://github.com/muselab-d2x/d2x/tree/cumulusci-next) branch contains a set of precontribution enhancements to CumulusCI we've encountered the need for in our consulting engagements. The end goal is to get all of these contributed back to CumulusCI. But, for now, the `cumulusci-next` branch and Docker image tag of D2X provides the following additional CumulusCI features:

* Scratch Org Snapshot Management (new)
* Package Version Naming with templated Jinja2 expressions
* Support for looking up 2gp feature test package commit statuses on parent branches
* A simple plugin framework for CumulusCI
* The ability to load arbitrary YAML

All these features are merged into [muselab-d2x/CumulusCI@d2x](https://github.com/muselab-d2x/CumulusCI)

The documentation below should all be assumed to apply to the `cumulusci-next` branch, using the `muselab-d2x/CumulusCI` fork as CumulusCI's codebase for now. Eventually the goal is to migrate these into the main branch when they are released in CumulusCI.

## Scratch Org Snapshot Management with D2X

D2X uses CumulusCI's `create_snapshot` and `github_pull_request_snapshot` tasks to automate the management of scratch org snapshots for the following uses cases:

* Maintaining a persistent named snapshot of the project's current dependencies, deployed into an org shape for either unpackaged or packaged deploy/install
* Maintaining a persistent named snapshot of the project's unpackaged code deployed into a non-namespaced scratch org for development
* Maintaining a persistent named snapshot of the project's current release, fully configured with storytelling data, in an org
  * Optionally maintain release snapshots for beta/prerelease versions, N+n versions, and past versions
* Maintain an temporary snapshot for the passing or failing build org state of a 2GP Feature Test build on a `feature/` branch

For more background on the complexities of automating snapshot management for these use cases, check out Muselab's blog post: [Develop, Test, and Fix Faster with Scratch Org Snapshots](https://muselab.com/bench-notes/develop-test-and-fix-faster-with-scratch-org-snapshots)

The snapshots functionality was generously contributed by [Veruna](https://veruna.com}, a Salesforce ISV Partner as part of D2X Transformation Success engagement with [Muselab](https://muselab.com/services).

### Snapshotting Dependencies

Coming soon!

### Snapshotting Unpackaged Source

Coming soon! NOTE: This will require the ability to deploy into a non-namespaced scratch org.

### Snapshotting Pull Requests

The first available resuable workflow for snapshot management is also one of the most valuable because it's designed to be used on every commit to every feature branch!

D2X's 2GP Feature Test reusable workflow already provides a ton of useful functionality to automate package testing including:

* Creating a new scratch org using the project's `feature` scratch org definition for CumulusCI
* Creating a new 2GP Feature Test package version of the commit via CumulusCI's built-in `build_feature_test_package` flow
  * Uses a separate 2GP package with the same namespace created automatically in the DevHub
  * Works with both 1GP and 2GP packages!
  * Uses `skipValidation` to create package versions in seconds without requiring a build scratch org
  * Read more about this process in Muselab's blog post [3 Approaches to Pre-Release Testing for Salesforce ISVs](https://muselab.com/bench-notes/3-approaches-to-pre-release-testing-for-salesforce-isvs).
* Setting a GitHub Commit Status on the commit, annotating it with description containing the test package version's id, such as `version_id: 04t...`
* Testing the new 2GP Feature Test package version in the build's `feature` scratch org via CumulusCI's built-in `ci_feature_2gp` flow
  * Install the 2GP Feature Test package version looked up from the commit status and dependencies using CumulusCI's built-in `install_2gp_commit` flow
  * Configure the package with CumulusCI's built-in `config_managed` flow
  * Run apex tests with CumulusCI's built-in `run_tests` including GitHub Job Summary reports for test executions
* Delete the build's `feature` scratch org

That's a lot out of the box. Just enabling this one workflow in your repository is a huge step and an even bigger improvement in productivity and quality if you get it right.

**So where do Scratch Org Snapshots fit into that workflow?**
With a default limit of 40 Active Snapshots and 40 Daily Snapshots for Enterprise Edition (matching your ActiveScratchOrg limit for both active and daily snapshots), efficient use of snapshots is important. You don't want to snapshot every commit or every branch or you'll likely hit your limits.

We've worked out what we believe is the ideal workflow for balancing limits and need:

1. Build every feature branch commit, as before
2. Use Pull Requests to control which branches get snapshots
3. Maintain a snapshot of the HEAD commit on all branches with Pull Requests matching the criteria
4. Use a common naming convention for snapshot names
5. Set the build and commit information in the description field of each OrgSnapshot record
6. Store the nameshot name as a GitHub Commit Status or Check on each commit with a snapshot

**Quickstart**

Assuming you already have CumulusCI configured for your project:

1. Add the new `ci_feature_2gp_pre_snapshot` and `ci_feature_2gp_post_snapshot` flows to allow split execution in the D2X reusable workflow by adding the following to your `cumulusci.yml` file and adapting for any changes your project has made to `ci_feature_2gp`:

```
flows:
   ci_feature_2gp_pre_snapshot:
        description: Pre-snapshot steps for 2gp feature test builds
        group: Continuous Integration
        steps:
            1:
                flow: install_2gp_commit
            2:
                flow: config_apextest_managed

    ci_feature_2gp_post_snapshot:
        description: Post-snapshot steps for 2gp feature test builds
        group: Continuous Integration
        steps:
            1:
                task: run_tests
```

2. Configure the `github_pull_request_snapshot` task's default options in `cumulusci.yml`

```
tasks:
    github_pull_request_snapshots:
        options:
            project_code: CI # Customize this!!!
            snapshot_pr: True
            snapshot_fail_pr: True
```

3. Set up the necessary secrets for D2X per the [Tutorial -> Secrets](tutorial.md#secrets)
4. Add the labels `snapshot` and `snapshot-failure` to the repository
5. Add the following file to your repository as `.github/workflows/feature_2gp.yml`

```
name: 2GP Feature Test and Snapshot
on:
  push:
    branches:
      - feature/**
      - main
  workflow_dispatch:

jobs:
  feature-test-and-snapshot:
    name: "Feature Test and Snapshot"
    uses: muselab-d2x/d2x/.github/workflows/feature-test-2gp-snapshot.yml@cumulusci-next
    with:
      create_pr_snapshot: true
      create_failure_snapshot: true
      environment_prefix: "Snapshot: "
      commit_status_context: Snapshot
    secrets:
      dev-hub-auth-url: "${{ secrets.DEV_HUB_AUTH_URL }}"
      gh-email: "${{ secrets.GH_EMAIL }}"
      github-token: "${{ secrets.GITHUB_TOKEN }}"
```

If your project uses CumulusCI's dependencies, you'll want to change the last line to `secrets.CCI_GITHUB_TOKEN`.

6. Commit to a branch like `feature/d2x-snapshots` and push to GitHub. The build should kick off under the Actions tab.
7. Before the build gets to actually deploying anything, create a Pull Request on the branch and add the `snapshot` and `snapshot-failure` labels to test it out


**In more detail**
Since building all branches with a Pull Request might also lead to a lot of snapshots, CumulusCI's new (currently in `muselab-d2x/CumulusCI` only via `d2x@cumulusci-next) `github_pull_request_snapshot` task provides a set of options you configure in your `cumulusci.yml` file:

* **project_code**: A 2-character uppercase code for the current project, used as a prefix on all snapshot names. *Must be unique to the DevHub*!
* **snapshot_pr**: Manage snapshots for the `HEAD` commit on branches with a matching Pull Request Default: `True`
* **snapshot_pr_label**: Only match branches with this label on the open Pull Request. Default: `snapshot`
* **snapshot_pr_draft**: Also create snapshots for open draft Pull Requests. Default: `False`
* **snapshot_failure_pr**: Manage snapshots for the latest unresolved build failure of branches with matching open Pull Request. Default: `False`
* **snapshot_failure_pr_label**: Only match branches with this label on the open Pull Request for failure snapshot creation. Default: `snapshot-failure`
* **snapshot_failure_pr_draft**: Also create failure snapshots for branches with an open matching Pull Request. Default: `False`
* **snapshot_failure_test_only**: Only snapshot failures due to test failures. Useful to limit to only prepared orgs with test failures to recreate test failure state. Default: `False`

There are also a set of options designed to be passed via `cci`:

* **--wait [True|False]**: If True, polls until the OrgSnapshot has completed and reports the results as one synchronous operation. When set to `False`, reports the InProgress snapshot info and outputs `SNAPSHOT_ID=<Id>` to `GITHUB_OUTPUT` if set, allowing future job steps to access the SNAPSHOT_ID to finalize the job with the `--snapshot-id` option. Default: `True`
* **--snapshot_id <OrgSnapshotId>**: Used for finalizing a snapshots created with `--wait False` to finalize the new snapshot later in the build
* **--build_success [True|False]**: Was the build a success? Default: `True`
* **--build_fail_tests [True|False]**: Did the build fail because of a test failure. Default: `False`
* **--snapshot-is-packaged [True|False]**: Is the source org for the snapshot meant for unpackaged deploys or packaged installs? Default: `False`
* **--commit-status <string>**: If set, sets a GitHub Commit Status or Check with the value as the context and the snapshot name as the value.



















