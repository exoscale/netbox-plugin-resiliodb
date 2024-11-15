from django.urls import path
from netbox.views.generic import ObjectChangeLogView
from . import models, views

urlpatterns = [
    # LCA Types
    path('lca-types/', views.LCATypeListView.as_view(), name='lcatype_list'),
    path('lca-types/add/', views.LCATypeEditView.as_view(), name='lcatype_add'),
    path('lca-types/<int:pk>/', views.LCATypeView.as_view(), name='lcatype'),
    path('lca-types/<int:pk>/edit/', views.LCATypeEditView.as_view(), name='lcatype_edit'),
    path('lca-types/<int:pk>/delete/', views.LCATypeDeleteView.as_view(), name='lcatype_delete'),
    path('lca-types/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='lcatype_changelog', kwargs={'model': models.LCAType}),

    # Indicators
    path('indicators/', views.IndicatorListView.as_view(), name='indicator_list'),
    path('indicators/add/', views.IndicatorEditView.as_view(), name='indicator_add'),
    path('indicators/<int:pk>/', views.IndicatorView.as_view(), name='indicator'),
    path('indicators/<int:pk>/edit/', views.IndicatorEditView.as_view(), name='indicator_edit'),
    path('indicators/<int:pk>/delete/', views.IndicatorDeleteView.as_view(), name='indicator_delete'),
    path('indicators/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='indicator_changelog', kwargs={'model': models.Indicator}),

    # Device Role LCA Type Mappings
    path('device-role-lca-mappings/', views.DeviceRoleLCATypeMappingListView.as_view(), name='devicerolelcatypemapping_list'),
    path('device-role-lca-mappings/add/', views.DeviceRoleLCATypeMappingEditView.as_view(), name='devicerolelcatypemapping_add'),
    path('device-role-lca-mappings/<int:pk>/', views.DeviceRoleLCATypeMappingView.as_view(), name='devicerolelcatypemapping'),
    path('device-role-lca-mappings/<int:pk>/edit/', views.DeviceRoleLCATypeMappingEditView.as_view(), name='devicerolelcatypemapping_edit'),
    path('device-role-lca-mappings/<int:pk>/delete/', views.DeviceRoleLCATypeMappingDeleteView.as_view(), name='devicerolelcatypemapping_delete'),
    path('device-role-lca-mappings/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='devicerolelcatypemapping_changelog', kwargs={'model': models.DeviceRoleLCATypeMapping}),

    # Site Country Mappings
    path('site-country-mappings/', views.SiteCountryMappingListView.as_view(), name='sitecountrymapping_list'),
    path('site-country-mappings/add/', views.SiteCountryMappingEditView.as_view(), name='sitecountrymapping_add'),
    path('site-country-mappings/<int:pk>/', views.SiteCountryMappingView.as_view(), name='sitecountrymapping'),
    path('site-country-mappings/<int:pk>/edit/', views.SiteCountryMappingEditView.as_view(), name='sitecountrymapping_edit'),
    path('site-country-mappings/<int:pk>/delete/', views.SiteCountryMappingDeleteView.as_view(), name='sitecountrymapping_delete'),
    path('site-country-mappings/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='sitecountrymapping_changelog', kwargs={'model': models.SiteCountryMapping}),

    # Plugin Settings
    path('settings/', views.PluginSettingsListView.as_view(), name='pluginsettings_list'),
    path('settings/add/', views.PluginSettingsEditView.as_view(), name='pluginsettings_add'),
    path('settings/<int:pk>/', views.PluginSettingsView.as_view(), name='pluginsettings'),
    path('settings/<int:pk>/edit/', views.PluginSettingsEditView.as_view(), name='pluginsettings_edit'),
    path('settings/<int:pk>/delete/', views.PluginSettingsDeleteView.as_view(), name='pluginsettings_delete'),
    path('settings/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='pluginsettings_changelog', kwargs={'model': models.PluginSettings}),
]
