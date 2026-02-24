# FastAPI Legacy Notes

This repository includes legacy FastAPI/WebSocket support paths for compatibility.

## Important

- FastAPI is **not required** for core Proxmox -> NetBox sync in the current plugin runtime.
- Core sync source of truth is `netbox_proxbox/services/proxmox_sync.py`.
- FastAPI-related components are retained as optional/legacy behavior and should be considered `needs review` before production use.

## When to Use

Only use FastAPI-related paths if you explicitly depend on legacy backend-service workflow in your deployment.

## Security/Operations

Treat all legacy FastAPI deployment snippets as non-authoritative unless reviewed for your environment.
Prefer NetBox-native plugin runtime and queued jobs where possible.
