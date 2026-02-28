# Required Parameters

The following fields are required on at least one Proxmox Endpoint before sync will work.

## Proxmox Endpoint — required fields

| Field | Example | Notes |
|---|---|---|
| `name` | `My Proxmox Cluster` | Arbitrary display name |
| `domain` | `proxmox.example.com` | Hostname or FQDN. At least one of `domain`/`ip_address` must be set. |
| `ip_address` | `192.168.1.10` | IP address. Can be used instead of or together with `domain`. |
| `username` | `root@pam` | Proxmox user in `user@realm` format |
| `password` | `s3cret` | Password auth. Required unless using API token. |
| `token_name` | `mytoken` | Token auth. Required together with `token_value` if not using password. |
| `token_value` | `xxxxxxxx-...` | Token value (UUID format) |

Either `password` **or** both `token_name` + `token_value` must be provided.

## Minimum NetBox configuration

```python
PLUGINS = ["proxmox2netbox"]
```

Migrations must be applied:

```bash
python manage.py migrate
python manage.py collectstatic --no-input
```
