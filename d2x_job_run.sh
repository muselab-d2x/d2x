#!/bin/bash -e

# Authenticate using Auth URL
echo "Authenticating to DevHub using auth url..."

# Write the DEV_HUB_AUTH_URL to a file
echo $DEV_HUB_AUTH_URL > /tmp/dev_hub_auth_url

# Authenticate the DevHub
sfdx org login sfdx-url -f /tmp/dev_hub_auth_url -a DevHub -d

d2x job run "$@"
