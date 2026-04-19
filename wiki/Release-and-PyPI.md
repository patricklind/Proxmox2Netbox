# Tags and Releases

## Maintainer: Release to PyPI

### 1) Bump version

Update both files to the same `X.Y.Z` version:

- `pyproject.toml` (`[project].version`)
- `proxmox2netbox/__init__.py` (`Proxmox2NetBoxConfig.version`)

### 2) Configure PyPI Trusted Publisher (OIDC)

In PyPI, configure a Trusted Publisher for:

- Owner: `patricklind`
- Repository: `Proxmox2Netbox`
- Workflow: `.github/workflows/publish-python-package.yml`
- Environment: `pypi`

### 3) Create release tag `vX.Y.Z`

Use either:

- GitHub Actions **Create Release Tag** workflow (manual, recommended), or
- Manual git commands:

```bash
git tag -a vX.Y.Z -m "Release vX.Y.Z"
git push origin vX.Y.Z
```

### 4) Workflow behavior

- `.github/workflows/release.yml` runs on tag push (`v*`), gates on lint/tests, and creates the GitHub Release.
- `.github/workflows/publish-python-package.yml` runs on `release: published` and publishes to PyPI.
- `.github/workflows/publish-python-package.yml` can also be triggered manually (`workflow_dispatch`) for retry.

### 5) Example: `v1.3.0`

```bash
git tag -a v1.3.0 -m "Release v1.3.0"
git push origin v1.3.0
```
