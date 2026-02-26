from netbox.plugins import PluginMenuButton, PluginMenuItem, PluginMenu

fullupdate_item = PluginMenuItem(
    link='plugins:proxmox2netbox:home',
    link_text='Full Update',
)

sync_processes_item = PluginMenuItem(
    link='plugins:proxmox2netbox:syncprocess_list',
    link_text='Sync Processes',
)

"""
    Endpoints Navigation Buttons.
"""
proxmox_endpoints_item = PluginMenuItem(
    link='plugins:proxmox2netbox:proxmoxendpoint_list',
    link_text='Proxmox Endpoints',
    buttons=(
        PluginMenuButton('plugins:proxmox2netbox:proxmoxendpoint_add', 'Add Proxmox Endpoint', 'mdi mdi-plus'),
    )
)

menu = PluginMenu(
    label='Proxmox2NetBox',
    groups=(
        ('Proxmox Plugin', (
                fullupdate_item,
                sync_processes_item,
            )
         ),
        ('Endpoints', (proxmox_endpoints_item,)),
    ),
    icon_class='mdi mdi-dns'
)
