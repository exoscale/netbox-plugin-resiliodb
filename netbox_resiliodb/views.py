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

class PluginSettingsListView(generic.ObjectListView):
    queryset = models.PluginSettings.objects.all()
    table = tables.PluginSettingsTable

class PluginSettingsView(generic.ObjectView):
    queryset = models.PluginSettings.objects.all()

class PluginSettingsEditView(generic.ObjectEditView):
    queryset = models.PluginSettings.objects.all()
    form = forms.PluginSettingsForm

class PluginSettingsDeleteView(generic.ObjectDeleteView):
    queryset = models.PluginSettings.objects.all()
