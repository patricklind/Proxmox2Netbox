# Installing and Starting Proxmox2NetBox-API

This guide will walk you through the steps to install and start the Proxmox2NetBox-API using pip.

## Prerequisites

- Python 3.10 or later installed on your system.
- pip, the Python package installer, should be installed.
- Virtual environment (optional but recommended).

## TL;DR

Here is a quick summary of the commands to install and start the Proxmox2NetBox-API (plugin backend):

```bash
# Create a directory for Proxmox2NetBox-API
mkdir /opt/proxmox2netbox-api
cd /opt/proxmox2netbox-api

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Proxmox2NetBox-API
pip install proxmox2netbox-api==0.0.2.post3

# Get the service file from GitHub repository
wget https://raw.githubusercontent.com/patricklind/Proxmox2NetBox/refs/heads/develop/contrib/proxmox2netbox.service /opt/proxmox2netbox-api/

# Copy the service file to systemd directory
sudo cp -v /opt/proxmox2netbox-api/proxmox2netbox.service /etc/systemd/system/

# Reload systemd and enable the service
sudo systemctl daemon-reload
sudo systemctl enable --now proxmox2netbox

# Check the status of the service
systemctl status proxmox2netbox

# If needed, start Proxmox2NetBox-API manually
/opt/proxmox2netbox-api/venv/bin/uvicorn proxbox_api.main:app --host 0.0.0.0 --port 8800
```

## Installation Steps

### Create a Virtual Environment:
   
It is recommended to use a virtual environment to manage dependencies. You can create one using the following command:

```bash
mkdir /opt/proxmox2netbox-api
cd /opt/proxmox2netbox-api
python3 -m venv venv
```
   
Activate the virtual environment:
   
```bash
source venv/bin/activate
```

### Install Proxmox2NetBox-API:

Use pip to install the Proxmox2NetBox-API package:

```bash
pip install proxmox2netbox-api==0.0.2.post3
```

## Starting Proxmox2NetBox-API

### systemd Setup

Get the service file from GitHub repository:

```
wget https://raw.githubusercontent.com/patricklind/Proxmox2NetBox/refs/heads/develop/contrib/proxmox2netbox.service /opt/proxmox2netbox-api/
```
Then copy `contrib/proxmox2netbox.service` to the `/etc/systemd/system/` directory.

```
sudo cp -v /opt/proxmox2netbox-api/proxmox2netbox.service /etc/systemd/system/
```

Once the configuration file has been saved, reload the service:

```
sudo systemctl daemon-reload
```

Then, start `proxmox2netbox` service and enable it to initiate at boot time:

```
sudo systemctl enable --now proxmox2netbox
```

You can use the command `systemctl status proxmox2netbox` to verify is FastAPI app is running:

```
systemctl status proxmox2netbox
```

This will start the Proxmox2NetBox-API server, and it will be ready to accept requests.

You should now be able to access `http://<YOUR-IP>:8800/docs`, like `http://127.0.0.1:8800/docs` (if localhost).

If any errors with the service, try starting Proxmox2NetBox-API server manually to check for more information or logs:

```bash
/opt/proxmox2netbox-api/venv/bin/uvicorn proxbox_api.main:app --host 0.0.0.0 --port 8800
```

## Troubleshooting

- If you encounter any issues during installation or startup, ensure that all dependencies are correctly installed and that your Python environment is properly configured.
- Check the Proxmox2NetBox-API logs for any error messages that might provide more insight into the problem.
