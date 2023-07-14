#!/bin/bash

if [ -f /tmp/dev_hub_authenticated ]; then
    exit 0
fi

echo "Authenticating to DevHub..."

# Write the DEV_HUB_AUTH_URL to a file
echo $DEV_HUB_AUTH_URL > /tmp/dev_hub_auth_url

# Authenticate the DevHub
sfdx org login sfdx-url -f /tmp/dev_hub_auth_url -a DevHub -d

# Ensure the force-app/main/default folder exists
mkdir -p force-app/main/default

rm /tmp/dev_hub_auth_url
touch /tmp/dev_hub_authenticated