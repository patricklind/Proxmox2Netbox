# Monitoring & Observability

## Sync process tracking

Every sync run creates a `SyncProcess` record in NetBox, visible via the plugin UI.

The record captures:
- Start and end time
- Endpoint synced
- Status (success / error)

## Job results

Background sync jobs are visible in NetBox under `Admin → Jobs`. The job result contains the sync summary and any errors encountered.

## Logs

Sync operations log at INFO level. Errors log at ERROR or WARNING.

When running from the CLI:

```bash
python manage.py netbox_unifi_sync_run --dry-run --json
```

Log output goes to stdout and the configured Django log handlers.

## What is NOT monitored

- Real-time Proxmox node status (CPU, memory utilization) is not polled.
- Proxmox alerts or HA events are not forwarded to NetBox.
- The plugin does not send webhooks or notifications — use NetBox's built-in webhook system for that.
