# Tags and Releases

Maintainer workflow for publishing `proxmox2netbox` to PyPI.

## 1) Bump the version

Before tagging a release, update version references to the same `X.Y.Z` value:

- `pyproject.toml` (`[project].version`)
- `proxmox2netbox/__init__.py` (`Proxmox2NetBoxConfig.version`)

> Note: This repository currently does **not** contain `netbox_unifi_sync/version.py` or `netbox-plugin.yaml`.

## 2) Configure PyPI Trusted Publisher (OIDC)

In PyPI for project `proxmox2netbox`, configure a Trusted Publisher for this repository/workflow:

- Owner: `patricklind`
- Repository: `Proxmox2Netbox`
- Workflow: `.github/workflows/publish-python-package.yml`
- Environment: `pypi`

## 3) Create release tag `vX.Y.Z`

Use one of these options:

- **GitHub Actions: Create Release Tag** (manual dispatch, recommended), or
- **Git manually**:

```bash
git tag -a vX.Y.Z -m "Release vX.Y.Z"
git push origin vX.Y.Z
```

## 4) Workflow behavior

- `.github/workflows/release.yml` runs on tag push (`v*`), gates on lint/tests, then creates the GitHub Release.
- `.github/workflows/publish-python-package.yml` runs on `release: published` and publishes to PyPI.
- `publish-python-package.yml` also supports manual `workflow_dispatch` for retry.

If the release is created by GitHub Actions with the repository `GITHUB_TOKEN`,
GitHub might not start the follow-up `release: published` publish workflow.
When that happens, run **Publish Python Package** manually from Actions for the
same tag.

## 5) Validate publish

```bash
pip install -U proxmox2netbox
python -c "import importlib.metadata as m; print(m.version('proxmox2netbox'))"
```
