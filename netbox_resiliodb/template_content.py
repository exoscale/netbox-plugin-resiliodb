from django.apps import apps
from django.conf import settings
from netbox.plugins import PluginTemplateExtension

def create_lcaparams_panel(self):
    return self.render('netbox_resiliodb/lcaparams_panel.html')

class DeviceTypeLCAParams(PluginTemplateExtension):
    model = 'dcim.devicetype'
    
    def right_page(self):
        return create_lcaparams_panel(self)

class DeviceLCAParams(PluginTemplateExtension):
    model = 'dcim.device'
    
    def right_page(self):
        return [create_lcaparams_panel(self)]

template_extensions = [DeviceTypeLCAParams, DeviceLCAParams]
