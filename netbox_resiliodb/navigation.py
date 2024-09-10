from netbox.plugins import PluginMenuItem

menu_items = (
    PluginMenuItem(
        link='plugins:netbox_resiliodb:lca_list',
        link_text='LCA Data',
        permissions=['netbox_resiliodb.view_lcadata']
    ),
)
