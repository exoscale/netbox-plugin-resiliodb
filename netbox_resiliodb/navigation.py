from netbox.plugins import PluginMenuItem, PluginMenu

menu_items = (
    PluginMenuItem(
        link='plugins:netbox_resiliodb:device_list',
        link_text='Devices',
        permissions=['dcim.view_device']
    ),
    PluginMenuItem(
        link='plugins:netbox_resiliodb:pluginsettings_list',
        link_text='Settings',
        permissions=['netbox_resiliodb.view_pluginsettings']
    ),
    PluginMenuItem(
        link='plugins:netbox_resiliodb:lcatype_list',
        link_text='LCA Types',
        permissions=['netbox_resiliodb.view_lcatype']
    ),
    PluginMenuItem(
        link='plugins:netbox_resiliodb:indicator_list',
        link_text='Indicators',
        permissions=['netbox_resiliodb.view_indicator']
    ),
    PluginMenuItem(
        link='plugins:netbox_resiliodb:devicerolelcatypemapping_list',
        link_text='Device Role Mappings',
        permissions=['netbox_resiliodb.view_devicerolelcatypemapping']
    ),
    PluginMenuItem(
        link='plugins:netbox_resiliodb:sitecountrymapping_list',
        link_text='Country Mappings',
        permissions=['netbox_resiliodb.view_sitecountrymapping']
    ),
)
