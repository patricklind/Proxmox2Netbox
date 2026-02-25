> **Proxmox2NetBox is under active development** and maintained on a **best-effort basis during my spare time**. At the moment, there is no commercial backing for the project. If you'd like to **help accelerate its progress**, you're very welcome to contribute by fixing issues, implementing features, and submitting a **[Pull Request](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-pull-requests)** for review.  

> I'd also like to express my **sincere gratitude to everyone who has contributed**, whether through code, bug reports, or feedback. Your help is what makes Proxmox2NetBox valuable and usable across many environments.

> If you'd like to further support my work, please consider **[sponsoring me](https://github.com/sponsors/emersonfelipesp)**. Thank you! 💖


## Netbox Plugin which integrates [Proxmox](https://www.proxmox.com/) and [Netbox](https://netbox.readthedocs.io/)! 🚀

> **⚠️ NOTE:** Proxmox2NetBox is currently under development and **only performs read-only operations using `GET` requests**. There is **no functionality implemented to modify or change your Proxmox environment**, so there's **no risk of unintentional changes** being made by the plugin at this stage.

### Versions 📌

The following table shows the Netbox and Proxmox versions compatible (tested) with Proxmox2NetBox plugin.

| [netbox version](https://github.com/netbox-community/netbox)   | proxmox version | [proxmox2netbox version](https://github.com/patricklind/Proxmox2NetBox) | [proxmox2netbox-api](https://github.com/emersonfelipesp/proxmox2netbox-api) | [pynetbox-api](https://github.com/emersonfelipesp/pynetbox-api) |
|------------------|-----------------|-----------------|--------------|--------------|
| =v4.2.6          | >=8.3.0         | v1.0.1          | v0.0.2.post3 | v0.0.2.post1 |
| =v4.2.6          | >=8.3.0         | v0.0.6b2        | v0.0.2       | v0.0.2       | 
| =v4.2.0          | >=8.3.0         | v0.0.6b1        | v0.0.1       | v0.0.1       | 
| >=v3.4.0         | >=v6.2.0        | =v0.0.5         |              |              |
| >=v3.2.0         | >=v6.2.0        | =v0.0.4         |              |              |
| >=v3.0.0 < v3.2  | >=v6.2.0        | =v0.0.3         |              |              |


## Installation 🛠️

### TL'DR (For Experienced Users)

#### Enable plugin in configuration.py (usually on /opt/netbox/netbox/netbox)

```
PLUGINS = ['netbox_proxbox']
```

### Run the commands to install plugin

```bash
# Activate virtual environment
source /opt/netbox/venv/bin/activate

# Install plugin
pip install proxmox2netbox

# Run migrations
cd /opt/netbox/netbox/
python3 manage.py migrate netbox_proxbox
python3 manage.py collectstatic --no-input

# Restart service
sudo systemctl restart netbox
```

### Setup the backend

The backend can be on a different venv (virtual environment) as it is a completely different service.
The communication between the plugin and its backend is fully through API.

```
pip install proxmox2netbox-api
uvicorn main:app --host 0.0.0.0 --port 8800
```

---

For detailed installation instructions, please refer to the following guides:

- [Installing using pip](./installation/1-installing-plugin.md) (recommended)
- [Installing using git](./installation/2-installing-plugin-git.md)
- [Installing using Docker](./installation/3-installing-plugin-docker.md)

---

## Stars History 📈

[![Star History Chart](https://api.star-history.com/svg?repos=patricklind/Proxmox2NetBox&type=Timeline)](https://star-history.com/#patricklind/Proxmox2NetBox&Timeline)
