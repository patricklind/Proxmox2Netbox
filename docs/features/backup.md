# Backups & Proxmox Backup Server

> **Not in scope.** Proxmox2NetBox does not integrate with Proxmox Backup Server (PBS) and does not sync backup jobs, schedules, or datastore status to NetBox.

## Current scope

This plugin is a one-way inventory sync: Proxmox → NetBox DCIM/IPAM.
It covers nodes, VMs, LXC containers, interfaces, and IP addresses.

Backup infrastructure (PBS datastores, backup jobs, retention policies) is not modelled in standard NetBox and is therefore out of scope.

## NetBox database backup

For backing up the NetBox PostgreSQL database itself, refer to standard PostgreSQL backup tooling (`pg_dump`, `pg_basebackup`) — this is unrelated to this plugin.
