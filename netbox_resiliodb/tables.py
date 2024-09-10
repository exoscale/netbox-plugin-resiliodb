import django_tables2 as tables
from netbox.tables import NetBoxTable, columns

from .models import LCAData

class LCADataTable(NetBoxTable):
    device_type = tables.Column(
        linkify=True,
        verbose_name='Device Type'
    )
    module_type = tables.Column(
        linkify=True,
        verbose_name='Module Type'
    )
    lca_type = tables.Column(
        verbose_name='LCA Type'
    )
    lca_pool = tables.Column(
        verbose_name='LCA Pool'
    )

    class Meta(NetBoxTable.Meta):
        model = LCAData
        fields = ('id', 'device_type', 'module_type', 'lca_type', 'lca_pool')
        default_columns = ('id', 'device_type', 'module_type', 'lca_type', 'lca_pool')
