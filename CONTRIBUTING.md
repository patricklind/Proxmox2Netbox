# Contributing to Proxbox

Thank you for contributing to Proxbox.

This project focuses on stable, predictable synchronization between Proxmox and NetBox. Contributions must preserve existing sync behavior unless a change is clearly documented, tested, and justified.

---

## Project Scope

Proxbox is a NetBox plugin that synchronizes Proxmox data into NetBox.

The sync process includes:

- Proxmox Nodes
- Virtual Machines
- Cluster information
- Interfaces
- Virtual Disks
- IP addresses assigned to interfaces (when possible)

All contributions must respect existing sync flow and data mapping principles.

---

## Sync Behavior Rules

The following must not be changed without explicit discussion and test coverage:

- Core sync orchestration logic
- API call sequence to Proxmox
- Data transformation/mapping logic
- Object matching logic in NetBox
- Update vs create behavior

If you modify anything related to these areas:

- Add or update tests
- Clearly document the behavioral change
- Justify why the change is required

---

## Virtual Disk Synchronization

Virtual disks are part of the sync and update process.

Contributors must ensure:

- Disks are linked to the correct Virtual Machine
- Disk size and relevant attributes are synchronized
- Updates in Proxmox are reflected in NetBox
- Disk changes do not break existing VM sync logic

Do not introduce destructive behavior (e.g. deleting disks in NetBox) without explicit safeguards.

---

## Interface IP Synchronization (Best Effort)

The sync process should attempt to assign IP addresses to interfaces when reliable data is available from Proxmox.

Rules:

- IP addresses must be attached to the correct interface
- Only create/update IPs if the data is valid and deterministic
- Sync must not fail if IP data is missing or ambiguous
- The system must remain stable even if IP detection fails

This feature must be implemented defensively.

---

## Development Guidelines

When contributing:

- Do not introduce breaking changes without documentation
- Maintain compatibility with current NetBox version
- Keep business logic separated from UI
- Do not hardcode configuration - use PLUGINS_CONFIG
- Follow existing project structure and naming conventions
- Keep changes minimal and focused

---

## Testing Requirements

Before submitting a pull request:

- Ensure the plugin loads correctly in NetBox
- Run all tests
- Add tests if you change Virtual Disk sync logic
- Add tests if you change Interface/IP assignment logic
- Add tests if you change mapping behavior
- Verify that no existing sync functionality regresses

Pull requests without passing tests will not be merged.

---

## Pull Request Process

Each PR should include:

- Clear description of changes
- Scope (bugfix, enhancement, refactor)
- Impact on sync behavior (if any)
- Confirmation that tests pass
- Risk assessment if sync logic was touched

---

## What Not To Do

- Do not change data models without migration review
- Do not change sync order unless absolutely required
- Do not remove existing functionality without justification
- Do not introduce experimental behavior into core sync path

If unsure whether something is safe to modify - open an issue first.

---

## Stability First

The priority of this project is reliable synchronization - not aggressive feature expansion.

All contributions must preserve predictability and runtime stability.
