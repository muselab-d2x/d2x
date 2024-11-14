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
        python3.12-dev && \
    \
    # Install pip for Python 3.12
    apt-get install -y --no-install-recommends python3-pip && \
    \
    # Set up python alternatives
    update-alternatives --install /usr/bin/python python /usr/bin/python3.12 1 && \
    update-alternatives --set python /usr/bin/python3.12 && \
    \
    ln -sf /usr/bin/pip3 /usr/bin/pip && \
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
RUN python --version

# Install GitHub CLI
RUN curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | gpg --dearmor -o /usr/share/keyrings/githubcli-archive-keyring.gpg && \
  echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | tee /etc/apt/sources.list.d/github-cli.list > /dev/null && \
  apt-get update && apt-get install -y gh

# Install CumulusCI
RUN pip --no-cache-dir install git+https://github.com/muselab-d2x/CumulusCI@d2x-merge-cci4 cookiecutter

# Copy devhub auth script and make it executable
COPY devhub.sh /usr/local/bin/devhub.sh
RUN chmod +x /usr/local/bin/devhub.sh

# Create d2x user
RUN useradd -r -m -s /bin/bash -c "D2X User" d2x

# Setup PATH
RUN echo 'export PATH=~/.local/bin:$PATH' >> /root/.bashrc && \
  echo 'export PATH=~/.local/bin:$PATH' >> /home/d2x/.bashrc && \
  echo '/usr/local/bin/devhub.sh' >> /root/.bashrc && \
  echo '/usr/local/bin/devhub.sh' >> /home/d2x/.bashrc

# # Stage for ChromeDriver
# FROM base AS chromedriver

# # Install ChromeDriver
# RUN apt-get install -y wget unzip && \
#   wget -O /tmp/chromedriver.zip https://chromedriver.storage.googleapis.com/$(curl -s https://chromedriver.storage.googleapis.com/LATEST_RELEASE)/chromedriver_linux64.zip && \
#   unzip /tmp/chromedriver.zip -d /usr/local/bin/ && \
#   rm /tmp/chromedriver.zip

# # Stage for Playwright
# FROM base AS playwright

# # Install Playwright
# RUN npm install -g playwright && \
#   npx playwright install

# Stage for full browser support (ChromeDriver + Playwright)
FROM base AS browser

# # Install ChromeDriver
# RUN apt-get install -y wget unzip && \
#   wget -O /tmp/chromedriver.zip https://chromedriver.storage.googleapis.com/$(curl -s https://chromedriver.storage.googleapis.com/LATEST_RELEASE)/chromedriver_linux64.zip && \
#   unzip /tmp/chromedriver.zip -d /usr/local/bin/ && \
#   rm /tmp/chromedriver.zip

# Install Playwright
RUN cci robot install_playwright \
  && npx playwright install-deps

# Final stage for no browser automation support
FROM base AS no-browser

USER d2x
CMD ["bash"]
