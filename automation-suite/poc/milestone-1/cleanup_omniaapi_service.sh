#!/bin/bash
# Copyright 2025 Dell Inc. or its subsidiaries. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Purpose:
# This script is used to clean up the Omnia API service, removing configuration files and stopping the service.

# Usage:
# The script can be run as root user with no arguments.

# Variables:
# SERVICE_NAME: The name of the service to clean up (omniaapi).
# SCRIPT_PATH: The path to the service script (/usr/local/bin/omniaapi.sh).
# SERVICE_FILE: The path to the service file (/etc/systemd/system/omniaapi.service).
# ENV_FILE: The path to the environment file (/etc/omniaapi.env).
# LOG_FILE: The path to the setup log file (/var/log/omniaapi_setup.log).
# SERVICE_LOG: The path to the service log file (/var/log/omniaapi.log).
# PORT: The port number used by the service (80).

# Exit Codes:
# 0: Successful execution.
# 1: Error occurred during execution.


SERVICE_NAME="omniaapi"
SCRIPT_PATH="/usr/local/bin/${SERVICE_NAME}.sh"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"
ENV_FILE="/etc/${SERVICE_NAME}.env"
LOG_FILE="/var/log/${SERVICE_NAME}_setup.log"
SERVICE_LOG="/var/log/${SERVICE_NAME}.log"
PORT=80

# Function for logging
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') : $1" | tee -a "$LOG_FILE"
}

# Check if running as root
if [[ $EUID -ne 0 ]]; then
    echo "ERROR: This script must be run as root."
    exit 1
fi

log "Starting cleanup process for $SERVICE_NAME..."

# Step 1: Stop and disable the service
if systemctl is-active --quiet "$SERVICE_NAME"; then
    log "Stopping service $SERVICE_NAME"
    systemctl stop "$SERVICE_NAME" || log "WARNING: Failed to stop service."
fi

if systemctl is-enabled --quiet "$SERVICE_NAME"; then
    log "Disabling service $SERVICE_NAME"
    systemctl disable "$SERVICE_NAME" || log "WARNING: Failed to disable service."
fi

# Step 2: Remove systemd service file
if [[ -f "$SERVICE_FILE" ]]; then
    log "Removing systemd service file: $SERVICE_FILE"
    rm -f "$SERVICE_FILE" || log "WARNING: Failed to remove service file."
fi

# Step 3: Remove application script
if [[ -f "$SCRIPT_PATH" ]]; then
    log "Removing application script: $SCRIPT_PATH"
    rm -f "$SCRIPT_PATH" || log "WARNING: Failed to remove application script."
fi

# Step 4: Remove environment file
if [[ -f "$ENV_FILE" ]]; then
    log "Removing environment file: $ENV_FILE"
    rm -f "$ENV_FILE" || log "WARNING: Failed to remove environment file."
fi

# Step 5: Remove logs
for file in "$LOG_FILE" "$SERVICE_LOG"; do
    if [[ -f "$file" ]]; then
        log "Removing log file: $file"
        rm -f "$file" || log "WARNING: Failed to remove log file $file."
    fi
done

# Step 6: Reload systemd daemon
log "Reloading systemd daemon"
systemctl daemon-reload || log "WARNING: Failed to reload systemd."

# Step 7: Close port 80 using firewalld (optional)
if systemctl is-active --quiet firewalld; then
    log "Removing firewall rule for port $PORT"
    firewall-cmd --permanent --remove-port=${PORT}/tcp || log "WARNING: Failed to remove port $PORT from firewall."
    firewall-cmd --reload || log "WARNING: Failed to reload firewall."
else
    log "firewalld is not active. Skipping firewall cleanup."
fi

log "Cleanup process completed for $SERVICE_NAME."
exit 0
