# Use the latest version of the d2x image
FROM ghcr.io/muselab-d2x/d2x:latest

# Set up bash prompt
USER d2x
COPY .devcontainer/pureline.conf ~/pureline.conf
RUN git clone https://github.com/chris-marsh/pureline.git ~/pureline \
    && cd ~/pureline && git reset --hard 9940906e824aae3a6f4bd0ee4dac2ea423d31089 \
    && echo 'if [ "$TERM" != "linux" ]; then\n    source ~/pureline/pureline ~/.pureline.conf\nfi' >> ~/.bashrc