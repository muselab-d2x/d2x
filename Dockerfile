FROM python:3.11-slim-bookworm

LABEL org.opencontainers.image.source = "https://github.com/muselab-d2x/d2x"

# Install sfdx
RUN \
  apt-get install -y wget gnupg && \
  wget -qO- https://deb.nodesource.com/gpgkey/nodesource.gpg.key | apt-key add - && \
  wget -qO- https://cli.github.com/packages/githubcli-archive-keyring.gpg | apt-key add - && \
  echo "deb https://deb.nodesource.com/node_20.x bullseye main" > /etc/apt/sources.list.d/nodesource.list && \
  echo "deb [arch=$(dpkg --print-architecture)] https://cli.github.com/packages stable main" > /etc/apt/sources.list.d/github-cli.list && \
  apt-get update && \
  apt-get install -y git nodejs gh && \
  rm -rf /var/lib/apt/lists/*

RUN npm install --global jq commander && npm install --global sfdx-cli --ignore-scripts 

# Install Salesforce CLI plugins:
RUN sfdx plugins:install @salesforce/sfdx-scanner

# Install CumulusCI
RUN python -m pip --no-cache-dir install cumulusci

# Copy devhub auth script and make it executable
COPY devhub.sh /usr/local/bin/devhub.sh
RUN chmod +x /usr/local/bin/devhub.sh

# Create d2x user
RUN useradd -r -s /sbin/nologin -m -c "D2X User" d2x

# Setup PATH
RUN echo 'export PATH=~/.local/bin:$PATH; source /usr/local/bin/devhub.sh' >> /home/d2x/.bashrc

USER d2x
CMD ["bash"]
