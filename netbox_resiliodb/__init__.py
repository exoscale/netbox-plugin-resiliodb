from netbox.plugins import PluginConfig
from pathlib import Path


class NetBoxResilioDBConfig(PluginConfig):
    name = 'netbox_resiliodb'
    verbose_name = 'Netbox ResilioDB'
    description = 'LCA footprint data sync from ResilioDB'
    version = '0.1'
    base_url = 'resiliodb'

    def ready(self):
        super().ready()
        # Register template directory
        self.template_dir = str(Path(__file__).parent / 'templates')


config = NetBoxResilioDBConfig
