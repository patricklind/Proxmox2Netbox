from netbox.plugins import PluginMenuButton, PluginMenuItem, PluginMenu
#from utilities.choices import ButtonColorChoices

fullupdate_item = PluginMenuItem(
    link='plugins:netbox_proxbox:home',
    link_text='Full Update',
)

sync_processes_item = PluginMenuItem(
    link='plugins:netbox_proxbox:syncprocess_list',
    link_text='Sync Processes',
)

backups_item = PluginMenuItem(
    link='plugins:netbox_proxbox:vmbackup_list',
    link_text='Backups',
)

contributing_item = PluginMenuItem(
    link='plugins:netbox_proxbox:contributing',
    link_text='Contributing!',
)

"""
    Endpoints Navigation Buttons.
"""
proxmox_endpoints_item = PluginMenuItem(
    link='plugins:netbox_proxbox:proxmoxendpoint_list',
    link_text='Proxmox Endpoints',
    buttons=(
        PluginMenuButton('plugins:netbox_proxbox:proxmoxendpoint_add', 'Add Proxmox Endpoint', 'mdi mdi-plus'),
    )
)

community_item = PluginMenuItem(
    link='plugins:netbox_proxbox:community',
    link_text='Community',
    buttons=[
        PluginMenuButton(
            "plugins:netbox_proxbox:discussions",
            "GitHub Discussions",
            "mdi mdi-github",
            #ButtonColorChoices.GRAY,
        ),
        PluginMenuButton(
            "plugins:netbox_proxbox:discord",
            "Discord Community",
            "mdi mdi-forum",
            #ButtonColorChoices.BLACK,
        ),
        PluginMenuButton(
            "plugins:netbox_proxbox:telegram",
            "Telegram Community",
            "mdi mdi-send",
            #ButtonColorChoices.BLUE,
        ),
    ]
)


menu = PluginMenu(
    label='Proxbox',
    groups=(
        ('Proxmox Plugin', (
                fullupdate_item,
                backups_item,
                sync_processes_item,
            )
         ),
        ('Endpoints', (proxmox_endpoints_item,)),
        ('Join our community', (contributing_item, community_item,)),
    ),
    icon_class='mdi mdi-dns'
)
