# Tags and Releases

## Maintainer: Release to PyPI

### 1) Bump version

Update these files to the same `X.Y.Z` value:

- `pyproject.toml` (`[project].version`)
- `proxmox2netbox/__init__.py` (`Proxmox2NetBoxConfig.version`)

### 2) Configure PyPI Trusted Publisher (OIDC)

Configure a PyPI Trusted Publisher for this repository/workflow:

- Owner: `patricklind`
- Repository: `Proxmox2Netbox`
- Workflow: `.github/workflows/publish-python-package.yml`
- Environment: `pypi`

### 3) Create tag `vX.Y.Z`

Choose one method:

- Via GitHub Actions **Create Release Tag** (manual) (**recommended**), or
- Manually with git:

```bash
git tag -a vX.Y.Z -m "Release vX.Y.Z"
git push origin vX.Y.Z
```

### 4) Workflow behavior

- `release.yml` runs on tag push, gates on lint/tests, and creates the GitHub Release.
- `publish-python-package.yml` runs on `release: published` and publishes to PyPI.
- `publish-python-package.yml` can also be run manually for retry.

### 5) Release `v1.3.0`

For this release, create and push:

```bash
git tag -a v1.3.0 -m "Release v1.3.0"
git push origin v1.3.0
```
