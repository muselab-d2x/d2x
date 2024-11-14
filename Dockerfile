# Base stage
FROM salesforce/cli:latest-full AS base

LABEL org.opencontainers.image.source="https://github.com/muselab-d2x/d2x"

# Install dependencies and Python 3.12
RUN apt-get update && \
    apt-get install -y --no-install-recommends software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        python3.12 \
        python3.12-venv \
        python3.12-dev \
        python3.12-distutils && \
    \
    # Install pip for Python 3.12 via get-pip.py
    curl -sS https://bootstrap.pypa.io/get-pip.py -o /tmp/get-pip.py && \
    python3.12 /tmp/get-pip.py && \
    rm /tmp/get-pip.py && \
    \
    # Create symbolic links for python and python3 to point to python3.12
    ln -sf /usr/bin/python3.12 /usr/bin/python && \
    ln -sf /usr/bin/python3.12 /usr/bin/python3 && \
    \
    # Create symbolic link for pip to /usr/bin/pip
    ln -sf /usr/local/bin/pip /usr/bin/pip && \
    \
    # Remove old Python 3.10 packages to save space
    apt-get remove -y --purge \
        python3.10 \
        python3.10-venv \
        python3.10-dev && \
    apt-get autoremove -y && \
    \
    # Clean up APT caches to reduce image size
    rm -rf /var/lib/apt/lists/*

# Verify Python installation
RUN python --version && \
    python3 --version && \
    pip --version

# Install GitHub CLI
RUN curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | gpg --dearmor -o /usr/share/keyrings/githubcli-archive-keyring.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | tee /etc/apt/sources.list.d/github-cli.list > /dev/null && \
    apt-get update && \
    apt-get install -y gh && \
    rm -rf /var/lib/apt/lists/*

# Install CumulusCI and Cookiecutter
RUN pip install --no-cache-dir git+https://github.com/muselab-d2x/CumulusCI@d2x-merge-cci4 cookiecutter

# Copy devhub auth script and make it executable
COPY devhub.sh /usr/local/bin/devhub.sh
RUN chmod +x /usr/local/bin/devhub.sh

# Create d2x user
RUN useradd -r -m -s /bin/bash -c "D2X User" d2x

# Setup PATH for root and d2x user
RUN echo 'export PATH=~/.local/bin:$PATH' >> /root/.bashrc && \
    echo 'export PATH=~/.local/bin:$PATH' >> /home/d2x/.bashrc && \
    echo '/usr/local/bin/devhub.sh' >> /root/.bashrc && \
    echo '/usr/local/bin/devhub.sh' >> /home/d2x/.bashrc

# Stage for full browser support (ChromeDriver + Playwright)
FROM base AS browser

# Install Playwright and its dependencies
RUN cci robot install_playwright && \
    npx playwright install-deps

# Final stage for no browser automation support
FROM base AS no-browser

# Switch to d2x user
USER d2x

# Default command
CMD ["bash"]
