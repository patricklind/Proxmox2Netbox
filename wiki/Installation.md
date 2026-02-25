# Installation

## Install package

```bash
pip install proxmox2netbox
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
