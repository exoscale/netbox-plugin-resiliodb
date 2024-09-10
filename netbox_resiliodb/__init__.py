from netbox.plugins import PluginConfig
from .navigation import menu_items

class NetBoxResilioDBConfig(PluginConfig):
    name = 'netbox_resiliodb'
    verbose_name = 'Netbox ResilioDB'
    description = 'LCA footprint data sync from ResilioDB'
    version = '0.1'
    base_url = 'resiliodb'

config = NetBoxResilioDBConfig
