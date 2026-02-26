# Installation

## Install package

```bash
pip install proxmox2netbox
```

For `netbox-docker`, also add it to `local_requirements.txt` so it persists after rebuild/redeploy:

```text
proxmox2netbox==1.1.0
```

## Enable plugin in NetBox

Add to `configuration.py`:

```python
PLUGINS = ["netbox_proxbox"]
```

## Apply plugin migration and static

```bash
python manage.py migrate netbox_proxbox
python manage.py collectstatic --no-input
```

## Open plugin UI

`Plugins -> Proxmox2NetBox`
