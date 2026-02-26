# Release and PyPI

## Version bump

Update both:

- `pyproject.toml` -> `[project].version`
- plugin source config -> plugin `version`

## Trusted Publisher (OIDC)

Configure in PyPI for project `proxmox2netbox`:

- Owner: `patricklind`
- Repository: `Proxmox2Netbox`
- Workflow: `.github/workflows/publish-python-package.yml`
- Environment: `pypi`

## Release steps

```bash
git tag -a vX.Y.Z -m "Release vX.Y.Z"
git push origin vX.Y.Z
```

Workflow behavior:

- `release.yml` creates GitHub Release from tag.
- `publish-python-package.yml` publishes package to PyPI.

## Validate publish

```bash
pip install -U proxmox2netbox
python -c "import importlib.metadata as m; print(m.version('proxmox2netbox'))"
```
