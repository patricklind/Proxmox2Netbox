#!/bin/bash

systemctl stop netbox.service

pip3 uninstall proxmox2netbox -y

python3 setup.py develop

systemctl start netbox.service
