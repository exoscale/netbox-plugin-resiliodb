from extras.plugins import PluginConfig

class NetBoxResilioDBConfig(PluginConfig):
    name = 'netbox_resiliodb'
    verbose_name = 'Netbox ResilioDB'
    description = 'LCA footprint data sync from ResilioDB'
    version = '0.1'
    base_url = 'resiliodb'

config = NetBoxResilioDBConfig
