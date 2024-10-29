# Base stage
FROM salesforce/cli:latest-full AS base

LABEL org.opencontainers.image.source="https://github.com/muselab-d2x/d2x"

# Install Python, Poetry, and GitHub CLI
RUN apt-get update && apt-get upgrade -y && apt-get install -y python3-pip curl gnupg && \
  curl -sSL https://install.python-poetry.org | python3 - && \
  echo "export PATH=$HOME/.local/bin:$PATH" >> /root/.bashrc && \
  curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | gpg --dearmor -o /usr/share/keyrings/githubcli-archive-keyring.gpg && \
  echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | tee /etc/apt/sources.list.d/github-cli.list > /dev/null && \
  apt-get update && apt-get install -y gh

# Ensure Poetry is in the PATH
ENV PATH="/root/.local/bin:$PATH"

# Copy d2x and CumulusCI pyproject.toml files
COPY pyproject.d2x.toml /usr/local/d2x/pyproject.toml
COPY pyproject.cci.toml /usr/local/cci/pyproject.toml

# Set up d2x environment
RUN cd /usr/local/d2x && \
  poetry install

# Set up CumulusCI environment
RUN cd /usr/local/cci && \
  poetry install

# Copy d2x source code
COPY d2x /usr/local/d2x

# Install CumulusCI and other Python packages
RUN pip --no-cache-dir install git+https://github.com/muselab-d2x/CumulusCI@1ae7db2af cookiecutter keyrings.alt

# Copy devhub auth script and make it executable
COPY devhub.sh /usr/local/bin/devhub.sh
RUN chmod +x /usr/local/bin/devhub.sh

# Create d2x user
RUN useradd -r -m -s /bin/bash -c "D2X User" d2x

# Set up PATH for both environments
ENV PATH="/usr/local/d2x/.venv/bin:/usr/local/cci/.venv/bin:$PATH"

# Verify installations
RUN python -c "import d2x" && \
  cci version

USER d2x
CMD ["bash"]