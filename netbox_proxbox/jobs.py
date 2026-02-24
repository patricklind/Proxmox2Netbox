"""NetBox job wrappers for Proxbox synchronization."""

from netbox.jobs import JobFailed, JobRunner

from netbox_proxbox.choices import SyncTypeChoices
from netbox_proxbox.services.proxmox_sync import (
    ProxmoxSyncError,
    sync_devices,
    sync_full_update,
    sync_virtual_machines,
)


class ProxboxSyncJob(JobRunner):
    """Run the existing Proxmox -> NetBox sync flow inside NetBox job queue."""

    class Meta:
        name = "Proxbox Sync"
        description = "Execute Proxmox synchronization using the plugin service layer"

    def run(self, sync_type: str = SyncTypeChoices.ALL):
        try:
            if sync_type == SyncTypeChoices.DEVICES:
                return sync_devices()
            if sync_type == SyncTypeChoices.VIRTUAL_MACHINES:
                return sync_virtual_machines()
            if sync_type == SyncTypeChoices.ALL:
                return sync_full_update()
            if sync_type == SyncTypeChoices.VIRTUAL_MACHINES_BACKUPS:
                raise JobFailed("VM backup sync is not available in out-of-the-box mode.")
            raise JobFailed(f"Unsupported sync_type: {sync_type}")
        except ProxmoxSyncError as exc:
            raise JobFailed(str(exc)) from exc


def enqueue_sync_job(sync_type: str = SyncTypeChoices.ALL):
    """Compatibility helper to enqueue the Proxbox sync job."""

    return ProxboxSyncJob.enqueue(sync_type=sync_type)
