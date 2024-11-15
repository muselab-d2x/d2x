# ========================
# Base Stage
# ========================
FROM python:3.12-slim AS base

LABEL org.opencontainers.image.source="https://github.com/muselab-d2x/d2x"

ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    gnupg \
    lsb-release \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    xz-utils \
    openjdk-17-jdk-headless \
    git \
    jq && \
    rm -rf /var/lib/apt/lists/*

# Install Node.js from NodeSource repository
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

# Ensure npm is at the latest version
RUN npm install -g npm@latest

# Ensure that /usr/local/lib/nodejs/bin is in PATH
ENV PATH="/usr/local/lib/nodejs/bin:${PATH}"

# Install Salesforce CLI via official TAR file
RUN curl -fsSL https://developer.salesforce.com/media/salesforce-cli/sf/channels/stable/sf-linux-x64.tar.xz -o sf-linux-x64.tar.xz && \
    mkdir -p /usr/local/sf && \
    tar xJf sf-linux-x64.tar.xz -C /usr/local/sf --strip-components 1 && \
    rm sf-linux-x64.tar.xz

# Ensure that sf CLI is in PATH
ENV PATH="/usr/local/sf/bin:${PATH}"

# Install pipx for isolated tool installations
RUN python -m pip install --upgrade pip && \
    python -m pip install --user pipx && \
    /root/.local/bin/pipx ensurepath

# Install CumulusCI and Cookiecutter using pipx (isolated environments)
RUN /root/.local/bin/pipx install "docutils" && \
    /root/.local/bin/pipx install "git+https://github.com/muselab-d2x/CumulusCI@d2x-merge-cci4" --include-deps && \
    /root/.local/bin/pipx install "cookiecutter"

# Copy devhub auth script and make it executable
COPY devhub.sh /usr/local/bin/devhub.sh
RUN chmod +x /usr/local/bin/devhub.sh

# Create d2x user
RUN useradd -r -m -s /bin/bash -c "D2X User" d2x

# Setup PATH for root and d2x user
RUN echo 'export PATH=~/.local/bin:$PATH' >> /root/.bashrc && \
    echo 'export PATH=~/.local/bin:$PATH' >> /home/d2x/.bashrc && \
    echo '/usr/local/bin/devhub.sh' >> /root/.bashrc && \
    echo '/usr/local/bin/devhub.sh' >> /home/d2x/.bashrc && \
    export PATH="/root/.local/bin:$PATH"

# ========================
# Browser Support Stage
# ========================
FROM base AS browser

# Install Playwright and its dependencies
RUN export PATH="/root/.local/bin:$PATH" && \
    /root/.local/bin/cci robot install_playwright && \
    npx playwright install-deps

# ========================
# No-Browser Stage
# ========================
FROM base AS no-browser

# Switch to d2x user
USER d2x

# Default command
CMD ["bash"]



