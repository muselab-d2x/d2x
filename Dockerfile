# ========================
# Base Stage
# ========================
FROM python:3.12-slim AS base

LABEL org.opencontainers.image.source="https://github.com/muselab-d2x/d2x"

ENV DEBIAN_FRONTEND=noninteractive

# Install minimal system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    git \
    openjdk-17-jdk-headless \
    xz-utils && \
    rm -rf /var/lib/apt/lists/*

# Install Node.js
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/* && \
    npm install -g npm@latest

# Install GitHub CLI
RUN curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | tee /etc/apt/sources.list.d/github-cli.list > /dev/null && \
    apt-get update && \
    apt-get install -y gh && \
    rm -rf /var/lib/apt/lists/*

# Install Salesforce CLI via official TAR file
RUN curl -fsSL https://developer.salesforce.com/media/salesforce-cli/sf/channels/stable/sf-linux-x64.tar.xz -o sf-linux-x64.tar.xz && \
    mkdir -p /usr/local/sf && \
    tar xJf sf-linux-x64.tar.xz -C /usr/local/sf --strip-components 1 && \
    rm sf-linux-x64.tar.xz

ENV PATH="/usr/local/sf/bin:/usr/local/bin:${PATH}"

# Install CumulusCI
RUN pip install --no-cache-dir \
    docutils \
    "git+https://github.com/muselab-d2x/CumulusCI@d2x" \
    cookiecutter

# Copy scripts directory and make scripts executable
COPY scripts /usr/local/bin/
RUN chmod +x /usr/local/bin/devhub.sh /usr/local/bin/parse_metadata_deletions.py /usr/local/bin/create_github_check.py

# Create d2x user, setup PATH for root and d2x user
RUN useradd -r -m -s /bin/bash -c "D2X User" d2x && \
    echo '/usr/local/bin/devhub.sh' >> /root/.bashrc && \
    echo '/usr/local/bin/devhub.sh' >> /home/d2x/.bashrc

# ========================
# Browser Support Stage
# ========================
FROM base AS browser

# Install Playwright and its dependencies
RUN cci robot install_playwright && \
    npx playwright install-deps

# ========================
# No-Browser Stage
# ========================
FROM base AS no-browser

# Switch to d2x user
USER d2x

# Default command
CMD ["bash"]
