#!/bin/bash
echo "Setting up cronjob for instance auto-shutdown"

# Get path to script
SCRIPT=$(readlink -f "$0")
SCRIPT_PATH=$(dirname "$SCRIPT")
echo "Current working dir: $PWD"
echo "Path to scripts: $SCRIPT_PATH"

# Add cron to check every 5min if instance is inactive
echo "Current crontab:"
crontab -l

# The file /etc/environment.sso stores the environment variables used by the API to authenticate to Azure services
echo "Adding crontab entry for instance auto-shutdown"
(crontab -l 2>/dev/null; echo "*/1 * * * * bash -l -c \"$SCRIPT_PATH/check_inactive.sh > /tmp/shutdown.log 2>&1\"") | crontab -

echo "New crontab:"
crontab -l
