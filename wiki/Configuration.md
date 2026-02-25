# Configuration

## Proxmox Endpoint

Create at least one endpoint in:

`Plugins -> Proxmox2NetBox -> Endpoints -> Proxmox Endpoints`

Required endpoint data:

- `name`
- `domain` and/or `ip_address`
- `username`
- `password` or (`token_name` + `token_value`)

Optional endpoint data:

- `port` (default `8006`)
- `verify_ssl`

## Authentication

Supported modes:

- Username + password
- Username + API token (`token_name`, `token_value`)

## Notes

- Plugin performs direct calls to Proxmox API from NetBox runtime.
- Missing optional fields should not block sync unless endpoint cannot authenticate.
