from netbox.plugins import PluginMenuButton, PluginMenuItem, PluginMenu

_PERMS = ['proxmox2netbox.view_proxmoxendpoint']

fullupdate_item = PluginMenuItem(
    link='plugins:proxmox2netbox:home',
    link_text='Full Update',
    permissions=_PERMS,
)

sync_processes_item = PluginMenuItem(
    link='plugins:proxmox2netbox:syncprocess_list',
    link_text='Sync Processes',
    permissions=_PERMS,
)

"""
    Endpoints Navigation Buttons.
"""
proxmox_endpoints_item = PluginMenuItem(
    link='plugins:proxmox2netbox:proxmoxendpoint_list',
    link_text='Proxmox Endpoints',
    permissions=_PERMS,
    buttons=(
        PluginMenuButton('plugins:proxmox2netbox:proxmoxendpoint_add', 'Add Proxmox Endpoint', 'mdi mdi-plus'),
    )
)

node_type_mappings_item = PluginMenuItem(
    link='plugins:proxmox2netbox:proxmoxnodetypemapping_list',
    link_text='Node Device Type Mappings',
    permissions=_PERMS,
    buttons=(
        PluginMenuButton('plugins:proxmox2netbox:proxmoxnodetypemapping_add', 'Add Mapping', 'mdi mdi-plus'),
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
        ('Configuration', (node_type_mappings_item,)),
    ),
    icon_class='mdi mdi-dns'
)
