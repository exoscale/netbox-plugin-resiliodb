import logging
from netbox.views import generic
from dcim.models import ModuleType
from . import models, tables, forms
from .cpu_data import CPUData

class LCATypeListView(generic.ObjectListView):
    queryset = models.LCAType.objects.all()
    table = tables.LCATypeTable

class LCATypeView(generic.ObjectView):
    queryset = models.LCAType.objects.all()

class LCATypeEditView(generic.ObjectEditView):
    queryset = models.LCAType.objects.all()
    form = forms.LCATypeForm

class LCATypeDeleteView(generic.ObjectDeleteView):
    queryset = models.LCAType.objects.all()

class IndicatorListView(generic.ObjectListView):
    queryset = models.Indicator.objects.all()
    table = tables.IndicatorTable

class IndicatorView(generic.ObjectView):
    queryset = models.Indicator.objects.all()

class IndicatorEditView(generic.ObjectEditView):
    queryset = models.Indicator.objects.all()
    form = forms.IndicatorForm

class IndicatorDeleteView(generic.ObjectDeleteView):
    queryset = models.Indicator.objects.all()

class DeviceRoleLCATypeMappingListView(generic.ObjectListView):
    queryset = models.DeviceRoleLCATypeMapping.objects.all()
    table = tables.DeviceRoleLCATypeMappingTable

class DeviceRoleLCATypeMappingView(generic.ObjectView):
    queryset = models.DeviceRoleLCATypeMapping.objects.all()

class DeviceRoleLCATypeMappingEditView(generic.ObjectEditView):
    queryset = models.DeviceRoleLCATypeMapping.objects.all()
    form = forms.DeviceRoleLCATypeMappingForm

class DeviceRoleLCATypeMappingDeleteView(generic.ObjectDeleteView):
    queryset = models.DeviceRoleLCATypeMapping.objects.all()

class SiteCountryMappingListView(generic.ObjectListView):
    queryset = models.SiteCountryMapping.objects.all()
    table = tables.SiteCountryMappingTable

class SiteCountryMappingView(generic.ObjectView):
    queryset = models.SiteCountryMapping.objects.all()

class SiteCountryMappingEditView(generic.ObjectEditView):
    queryset = models.SiteCountryMapping.objects.all()
    form = forms.SiteCountryMappingForm

class SiteCountryMappingDeleteView(generic.ObjectDeleteView):
    queryset = models.SiteCountryMapping.objects.all()

from django.shortcuts import redirect
from django.urls import reverse

class PluginSettingsListView(generic.ObjectListView):
    queryset = models.PluginSettings.objects.all()
    table = tables.PluginSettingsTable

    def get(self, request):
        # Redirect to the single instance
        instance = models.PluginSettings.objects.first()
        if instance:
            return redirect('plugins:netbox_resiliodb:pluginsettings', pk=instance.pk)
        return super().get(request)

class PluginSettingsView(generic.ObjectView):
    queryset = models.PluginSettings.objects.all()

class PluginSettingsEditView(generic.ObjectEditView):
    queryset = models.PluginSettings.objects.all()
    form = forms.PluginSettingsForm

    def get_object(self, **kwargs):
        return models.PluginSettings.objects.get(pk=1)

    def get(self, request, *args, **kwargs):
        try:
            return super().get(request, *args, **kwargs)
        except models.PluginSettings.DoesNotExist:
            # Create default instance if it doesn't exist
            obj = models.PluginSettings(pk=1)
            obj.save()
            return super().get(request, *args, **kwargs)

class PluginSettingsDeleteView(generic.ObjectDeleteView):
    queryset = models.PluginSettings.objects.all()

    def get(self, request, *args, **kwargs):
        # Prevent access to delete view
        return redirect('plugins:netbox_resiliodb:pluginsettings', pk=1)

class LCAParamsView(generic.ObjectView):
    queryset = models.LCAParams.objects.all()

class LCAParamsEditView(generic.ObjectEditView):
    queryset = models.LCAParams.objects.all()
    form = forms.LCAParamsForm
    template_name = 'netbox_resiliodb/lcaparams_edit.html'

    def alter_object(self, instance, request, args, kwargs):
        if not instance.pk:
            # Assign the parent object based on URL kwargs
            content_type_id = request.GET.get('content_type')
            object_id = request.GET.get('object_id')

            if content_type_id and object_id:
                instance.content_type_id = content_type_id
                instance.object_id = object_id

                # Get the parent object
                parent = instance.content_object
                if parent:
                    if isinstance(parent, ModuleType):  # It's a ModuleType
                        # Get default parameters based on module type tags
                        if parent.tags.all():
                            for tag in parent.tags.all():
                                tag_name = tag.name.upper()
                                if tag_name == 'CPU':
                                    # Get CPU name from module type model name
                                    cpu_name = parent.model
                                    cpu_specs = CPUData.get_cpu_specs(cpu_name)
                                    instance.parameters = {
                                        "name": cpu_name,
                                        "litho_nm": cpu_specs['litho_nm'],
                                        "die_surface_mm2": cpu_specs['die_surface_mm2']
                                    }
                                    break
                                elif tag_name == 'SSD':
                                    instance.parameters = {
                                        "casing": "casing_M2",
                                        "size_gb": 564,
                                        "technology": "TLC"
                                    }
                                    break
                                elif tag_name == 'RAM':
                                    instance.parameters = {
                                        "size_gb": 8
                                    }
                                    break
                                elif tag_name == 'GPU':
                                    instance.parameters = {
                                        "die_surface_mm2": 200,
                                        "litho_nm": 22
                                    }
                                    break
                                # HDD just needs the tag, no parameters needed
                    elif hasattr(parent, 'role'):  # It's a Device
                        # Look for a matching LCA type for the device role
                        mapping = models.DeviceRoleLCATypeMapping.objects.filter(
                            device_role=parent.role
                        ).first()
                        if mapping and mapping.lca_type.default_payload:
                            instance.parameters = mapping.lca_type.default_payload
                    elif hasattr(parent, 'instances'):  # It's a DeviceType
                        # Find first device of this type that has a role with LCA mapping
                        device = parent.instances.first()
                        if device and device.role:
                            mapping = models.DeviceRoleLCATypeMapping.objects.filter(
                                device_role=device.role
                            ).first()
                            if mapping and mapping.lca_type.default_payload:
                                instance.parameters = mapping.lca_type.default_payload
        return instance

    def get_return_url(self, request, obj=None):
        return request.GET.get('return_url') or super().get_return_url(request, obj)

class LCAParamsDeleteView(generic.ObjectDeleteView):
    queryset = models.LCAParams.objects.all()
