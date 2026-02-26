# Installing the Plugin using pip

## 1. Activate NetBox virtual environment

```bash
source /opt/netbox/venv/bin/activate
```

## 2. Install package

```bash
pip install proxmox2netbox
```

## 3. Enable plugin

Edit `/opt/netbox/netbox/netbox/configuration.py`:

```python
PLUGINS = ["proxmox2netbox"]
```

## 4. Run migrations and collect static files

```bash
cd /opt/netbox/netbox/
python3 manage.py migrate
python3 manage.py collectstatic --no-input
```

## 5. Restart NetBox

```bash
sudo systemctl restart netbox
```

## 6. Configure Proxmox endpoint and run sync

In NetBox UI:

- `Plugins -> Proxmox2NetBox -> Endpoints -> Proxmox Endpoints`
- Create endpoint with username and either password or API token.
- Run `Sync Nodes`, `Sync Virtual Machines`, or `Full Update Sync` from plugin home.
