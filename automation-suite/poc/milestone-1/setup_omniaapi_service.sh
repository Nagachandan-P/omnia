#!/bin/bash

SERVICE_NAME="omniaapi"
SCRIPT_PATH="/usr/local/bin/${SERVICE_NAME}.sh"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"
ENV_FILE="/etc/${SERVICE_NAME}.env"
LOG_FILE="/var/log/${SERVICE_NAME}_setup.log"
SERVICE_LOG="/var/log/${SERVICE_NAME}.log"
CWD=$(pwd)
PORT=80

# Function for logging
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') : $1" | tee -a "$LOG_FILE"
}

# Check if running as root
if [[ $EUID -ne 0 ]]; then
    log "ERROR: This script must be run as root."
    exit 1
fi

# Step 1: Verify RHEL 10
OS_ID=$(grep '^ID=' /etc/os-release | cut -d= -f2 | tr -d '"')
OS_VERSION=$(grep '^VERSION_ID=' /etc/os-release | cut -d= -f2 | tr -d '"')

if [[ "$OS_ID" != "rhel" || $(echo "$OS_VERSION" | cut -d. -f1) -lt 10 ]]; then
    log "ERROR: This script is intended for RHEL 10 only. Detected: $OS_ID $OS_VERSION"
    exit 1
fi
log "Verified RHEL 10 system."

# Step 2: Install Python3 if missing
if ! command -v python3 &>/dev/null; then
    log "Installing Python3..."
    if ! yum install -y python3 python3-pip; then
        log "ERROR: Failed to install Python3."
        exit 1
    fi
else
    log "Python3 is already installed."
fi

# Step 2.5: Install packages from requirements.txt
if [ -f requirements.txt ]; then
    log "Installing packages from requirements.txt..."
    if ! python3 -m pip install -r requirements.txt; then
        log "ERROR: Failed to install packages from requirements.txt."
        exit 1
    fi
else
    log "requirements.txt not found. Skipping installation of packages."
fi

# Step 3: Install FastAPI and Uvicorn
log "Installing FastAPI and Uvicorn..."
if ! python3 -m pip install --upgrade pip; then
    log "ERROR: Failed to upgrade pip."
    exit 1
fi
if ! python3 -m pip install fastapi uvicorn; then
    log "ERROR: Failed to install FastAPI and Uvicorn."
    exit 1
fi

# Step 4: Validate FastAPI app path
APP_PATH="$1"
if [[ -n "$APP_PATH" && ! -f "$APP_PATH" ]]; then
    log "ERROR: Provided FastAPI app file does not exist: $APP_PATH"
    exit 1
fi

# Extract directory and module name if APP_PATH provided
if [[ -n "$APP_PATH" ]]; then
    APP_DIR=$(dirname "$APP_PATH")
    APP_MODULE=$(basename "$APP_PATH" .py)
fi

# Step 5: Create environment file
log "Creating environment file at $ENV_FILE"
cat <<EOF > "$ENV_FILE"
OMNIA_ENV="production"
OMNIA_DEBUG="false"
EOF

# Step 6: Create application script
log "Creating application script at $SCRIPT_PATH"
if [[ -n "$APP_PATH" ]]; then
    cat <<EOF > "$SCRIPT_PATH"
#!/bin/bash
source $ENV_FILE
cd $APP_DIR
exec python3 -m uvicorn ${APP_MODULE}:app --host 0.0.0.0 --port $PORT
EOF
else
    cat <<EOF > "$SCRIPT_PATH"
#!/bin/bash
source $ENV_FILE
cd $CWD
exec python3 -m uvicorn api_server:app --host 0.0.0.0 --port $PORT
EOF
fi

#cat <<EOF > "$SCRIPT_PATH"
#!/bin/bash
#source $ENV_FILE
#if [[ -n "$APP_PATH" ]]; then
#    cd $APP_DIR
#    exec python3 -m uvicorn ${APP_MODULE}:app --host 0.0.0.0 --port $PORT
#else
#    exec python3 -m uvicorn api_server:app --host 0.0.0.0 --port $PORT
#fi
#EOF
chmod +x "$SCRIPT_PATH"

# Step 7: Create systemd service file
log "Creating systemd service file at $SERVICE_FILE"
cat <<EOF > "$SERVICE_FILE"
[Unit]
Description=OmniaAPI FastAPI Service
After=network.target

[Service]
ExecStart=$SCRIPT_PATH
Restart=on-failure
RestartSec=5
StartLimitIntervalSec=60
StartLimitBurst=3
EnvironmentFile=$ENV_FILE
StandardOutput=append:$SERVICE_LOG
StandardError=append:$SERVICE_LOG
User=root

[Install]
WantedBy=multi-user.target
EOF

# Step 8: Reload systemd
log "Reloading systemd daemon"
systemctl daemon-reload || { log "ERROR: Failed to reload systemd."; exit 1; }

# Step 9: Enable and start service
log "Enabling and starting service $SERVICE_NAME"
systemctl enable "$SERVICE_NAME" || { log "ERROR: Failed to enable service."; exit 1; }
systemctl start "$SERVICE_NAME" || { log "ERROR: Failed to start service."; exit 1; }

# Step 10: Open port 80 using firewalld
log "Configuring firewall to allow port $PORT"
if systemctl is-active --quiet firewalld; then
    if ! firewall-cmd --query-port=${PORT}/tcp; then
        firewall-cmd --permanent --add-port=${PORT}/tcp || { log "ERROR: Failed to add port $PORT."; exit 1; }
        firewall-cmd --reload || { log "ERROR: Failed to reload firewall."; exit 1; }
        log "Port $PORT opened successfully."
    fi
else
    log "WARNING: firewalld is not active. Please ensure port $PORT is open manually."
fi

# Step 11: Verify service status
if systemctl is-active --quiet "$SERVICE_NAME"; then
    log "SUCCESS: Service $SERVICE_NAME is active and running on port $PORT."
else
    log "ERROR: Service $SERVICE_NAME is not running."
    exit 1
fi

exit 0
