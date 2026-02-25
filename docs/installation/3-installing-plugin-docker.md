# Installing the Plugin using Docker

Docker install instructions for this repository are not finalized yet.

Current recommendation:

- Install through NetBox container shell with `pip install proxmox2netbox`, or
- Build your own image that includes this plugin, then run:

```bash
python3 manage.py migrate netbox_proxbox
python3 manage.py collectstatic --no-input
```

No external backend service is required.
