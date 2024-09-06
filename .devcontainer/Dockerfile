# Use the latest version of the d2x image
FROM ghcr.io/muselab-d2x/d2x:latest

# Set up bash prompt
USER d2x
COPY .devcontainer/pureline.conf ~/pureline.conf
RUN git clone https://github.com/chris-marsh/pureline.git ~/pureline \
    && cd ~/pureline && git reset --hard 9940906e824aae3a6f4bd0ee4dac2ea423d31089 \
    && echo 'if [ "$TERM" != "linux" ]; then\n    source ~/pureline/pureline ~/.pureline.conf\nfi' >> ~/.bashrc

RUN sudo apt-key del 23F3D4EA75716059 || true
  
RUN curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg

  # Update GitHub CLI repository list
RUN echo "deb [signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null

  # Add NodeSource GPG key for Node.js 20.x
RUN curl -fsSL https://deb.nodesource.com/gpgkey/nodesource.gpg.key | sudo tee /usr/share/keyrings/nodesource.gpg > /dev/null

  # Update NodeSource repository list
RUN echo "deb [signed-by=/usr/share/keyrings/nodesource.gpg] https://deb.nodesource.com/node_20.x bullseye main" | sudo tee /etc/apt/sources.list.d/nodesource.list > /dev/null

  # Update packages list
RUN sudo apt-get update