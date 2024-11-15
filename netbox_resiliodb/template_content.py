from django.apps import apps
from django.conf import settings
from netbox.plugins import PluginTemplateExtension

def create_lcaparams_panel(self):
    try:
        return self.render('netbox_resiliodb/lcaparams_panel.html')
    except Exception as e:
        return f"<!-- Error rendering LCA params panel: {str(e)} -->"

class DeviceTypeLCAParams(PluginTemplateExtension):
    model = 'dcim.devicetype'
    
    def right_page(self):
        return create_lcaparams_panel(self)

class DeviceLCAParams(PluginTemplateExtension):
    model = 'dcim.device'
    
    def right_page(self):
        return [create_lcaparams_panel(self)]

template_extensions = [DeviceTypeLCAParams, DeviceLCAParams]
