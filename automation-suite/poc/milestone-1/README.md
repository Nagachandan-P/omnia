# OmniaAPI Service Setup Script

## Overview
`setup_omniaapi_service.sh` is an automated script designed to:
- Verify the system is running **RHEL 10**.
- Install **Python3**, **pip**, **FastAPI**, and **Uvicorn** if not already installed.
- Accept a fully qualified path to your api_server.py application file. (e.g., Give the full path of checkout code of api_server.py. If the omnia code is checked out at root directory, give the path as /root/omnia/automation-suite/poc/milestone-1/api_server.py)
- Create an environment file at `/etc/OmniaAPI.env`.
- Generate a systemd service named `omniaapi` with:
  - Auto-restart on failure.
  - Logging to `/var/log/OmniaAPI.log`.
  - Environment variables support.
- Open **port 80** using `firewalld`.
- Enable and start the service automatically.

## Prerequisites
- RHEL 10 operating system.
- Root privileges.
- `firewalld` service running (for opening port 80).


## Features
- **Dynamic App Path**: Provide the full path to your FastAPI app file.
- **Logging**: Setup actions logged to `/var/log/OmniaAPI_setup.log`.
- **Restart Policy**: Service restarts on failure with limits.

## Usage
1. Invoke the script setup_omniaapi_service.sh

2. Make the script executable:
   ```bash
   chmod +x setup_omniaapi_service.sh
   ```

3. Run the script with the full path to your FastAPI app file:
   ```bash
   sudo ./setup_omniaapi_service.sh /opt/omniaapi/main.py
   ```

## What Happens After Running?
- The script installs required dependencies.
- Creates `/etc/omniaapi.env` for environment variables.
- Creates `/usr/local/bin/omniaapi.sh` to start Uvicorn.
- Creates `/etc/systemd/system/omniaapi.service` for systemd.
- Opens port 80 via `firewalld`.
- Enables and starts the `omniaapi` service.

## Verify Service Status
```bash
systemctl status omniaapi
```

## Logs
- Setup log: `/var/log/omniaapi_setup.log`
- Service log: `/var/log/omniaapi.log`

## Notes
- If `firewalld` is not active, manually open port 80.

## API Endpoints

The `omniaapi` service exposes the following endpoints:

### 1. Parse Catalog (`/ParseCatalog`)
Parses a catalog JSON file and generates root JSON files.

**Method:** POST

```bash
curl -X POST -F "file=@/path/to/catalog.json" http://localhost:80/ParseCatalog
```

**Example:**
```bash
curl -X POST -F "file=@catalog_parser/test_fixtures/catalog_rhel.json" http://localhost:80/ParseCatalog
```

**Response:**
```json
{"message": "Catalog parsed successfully"}
```

### 2. Generate Input Files (`/GenerateInputFiles`)
Generates omnia configuration files from a catalog JSON file.

**Method:** POST

```bash
curl -X POST -F "file=@/path/to/catalog.json" http://localhost:80/GenerateInputFiles
```

**Example:**
```bash
curl -X POST -F "file=@catalog_parser/test_fixtures/catalog_rhel.json" http://localhost:80/GenerateInputFiles
```

**Response:**
```json
{"message": "Input files generated successfully"}
```

### 3. Build Image (`/BuildImage`)
Triggers the build image process by executing the build_image playbook.

**Method:** POST

```bash
curl -X POST http://localhost:80/BuildImage
```

**Response:**
```json
{"message": "Invoked BuildImage Successfully"}
```

