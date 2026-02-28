# Upgrading Proxmox2NetBox

## From PyPI (recommended)

```bash
source /opt/netbox/venv/bin/activate
pip install --upgrade proxmox2netbox
cd /opt/netbox/netbox/
python manage.py migrate
python manage.py collectstatic --no-input
sudo systemctl restart netbox netbox-rq
```

## From git checkout (editable install)

```bash
cd /path/to/Proxmox2Netbox
git pull
cd /opt/netbox/netbox/
python manage.py migrate
python manage.py collectstatic --no-input
sudo systemctl restart netbox netbox-rq
```

## After upgrading

- Run `python manage.py showmigrations proxmox2netbox` to confirm all migrations applied.
- Open `Plugins -> Proxmox2NetBox` and verify the plugin loads correctly.
- Run a sync to verify data is still correct.

## Notes

- Always apply migrations after upgrading — new versions may add database columns or tables.
- If using an editable install (`pip install -e`), Django will pick up code changes automatically after a service restart without reinstalling.
