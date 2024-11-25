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

class DeviceTypeLCAParams(PluginTemplateExtension):
    model = 'dcim.devicetype'

    def right_page(self):
        return create_lcaparams_panel(self)

class DeviceLCAParams(PluginTemplateExtension):
    model = 'dcim.device'

    def right_page(self):
        return create_lcaparams_panel(self)

class ModuleTypeLCAParams(PluginTemplateExtension):
    model = 'dcim.moduletype'

    def right_page(self):
        return create_lcaparams_panel(self)


class DeviceSyncButton(PluginTemplateExtension):
    model = 'dcim.device'

    def buttons(self):
        return self.render('netbox_resiliodb/sync_button.html')

template_extensions = [DeviceTypeLCAParams, DeviceLCAParams, ModuleTypeLCAParams, DeviceSyncButton]
