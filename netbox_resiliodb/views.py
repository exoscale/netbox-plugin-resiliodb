from netbox.views import generic
from . import models, tables, forms

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

        return instance

    def get_return_url(self, request, obj=None):
        return request.GET.get('return_url') or super().get_return_url(request, obj)

class LCAParamsDeleteView(generic.ObjectDeleteView):
    queryset = models.LCAParams.objects.all()
