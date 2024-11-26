import logging
from django.apps import apps
from django.conf import settings
from netbox.plugins import PluginTemplateExtension

def create_lcaparams_panel(self):
    try:
        return self.render('netbox_resiliodb/lcaparams_panel.html', extra_context={
            'object': self.context['object'],
            'request': self.context['request']
        })
    except Exception as e:
        logging.error(f"Error rendering LCA params panel: {str(e)}")
        return ""

def create_lcafootprint_panel(self):
    try:
        impact_data = []
        gwp_data = None
        wu_data = None
        
        if hasattr(self.context['object'], 'lca_impact_data'):
            lca_data = self.context['object'].lca_impact_data
            if lca_data:
                for value in lca_data.indicator_values.all():
                    data = {
                        'indicator': value.indicator.code,
                        'unit': value.indicator.unit,
                        'total': value.total_value,
                        'steps': {
                            'BLD': value.BLD or 0,
                            'DIS': value.DIS or 0,
                            'USE': value.USE or 0,
                            'EOL': value.EOL or 0
                        }
                    }
                    impact_data.append(data)
                    
                    # Store GWP and WU data separately
                    if value.indicator.code == 'GWP':
                        gwp_data = data
                    elif value.indicator.code == 'WU':
                        wu_data = data

        return self.render('netbox_resiliodb/lcafootprint_panel.html', extra_context={
            'object': self.context['object'],
            'request': self.context['request'],
            'impact_data': impact_data,
            'gwp_data': gwp_data,
            'wu_data': wu_data
        })
    except Exception as e:
        logging.error(f"Error rendering LCA params panel: {str(e)}")
        return ""

class DeviceTypeLCAParams(PluginTemplateExtension):
    model = 'dcim.devicetype'

    def right_page(self):
        return create_lcaparams_panel(self)

class DeviceLCAParams(PluginTemplateExtension):
    model = 'dcim.device'

    def right_page(self):
        return create_lcaparams_panel(self)

class DeviceFootprintParams(PluginTemplateExtension):
    model = 'dcim.device'

    def left_page(self):
        return create_lcafootprint_panel(self)

class ModuleTypeLCAParams(PluginTemplateExtension):
    model = 'dcim.moduletype'

    def right_page(self):
        return create_lcaparams_panel(self)


class DeviceSyncButton(PluginTemplateExtension):
    model = 'dcim.device'

    def buttons(self):
        return self.render('netbox_resiliodb/sync_button.html')

template_extensions = [DeviceTypeLCAParams, DeviceLCAParams, ModuleTypeLCAParams, DeviceSyncButton, DeviceFootprintParams]
