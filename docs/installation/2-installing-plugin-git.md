# Installing the Plugin using Git

## 1. Clone repository

```bash
cd /opt/netbox/netbox/netbox
git clone https://github.com/patricklind/Proxmox2NetBox.git
cd Proxmox2NetBox
```

## 2. Activate NetBox virtual environment

```bash
source /opt/netbox/venv/bin/activate
```

## 3. Install plugin package

```bash
pip install .
```

## 4. Enable plugin

Edit `/opt/netbox/netbox/netbox/configuration.py`:

```python
PLUGINS = ['netbox_proxbox']
```

## 5. Run migrations and collect static files

```bash
cd /opt/netbox/netbox/
python3 manage.py migrate netbox_proxbox
python3 manage.py collectstatic --no-input
```

## 6. Restart NetBox

```bash
sudo systemctl restart netbox
```

## 7. Configure Proxmox endpoint and run sync

Use plugin UI to configure credentials and run sync operations.
