# Troubleshooting

## Plugin page returns server error

1. Check NetBox logs.
2. Verify migrations:

```bash
python manage.py showmigrations
```

3. Validate plugin config:

```bash
python manage.py check
```

## Endpoint save fails

- Ensure either password auth or token auth fields are complete.
- Verify Proxmox host/port is reachable from NetBox container.

## Sync runs but data missing

- Confirm endpoint credentials have API access.
- Check whether Proxmox actually exposes interface/IP details.
- IP sync is best effort and intentionally non-fatal.

## PyPI release did not publish

- Confirm tag format is `vX.Y.Z`.
- Confirm GitHub Release was created.
- Confirm trusted publisher binding in PyPI matches repo/workflow/environment.
