from django.urls import path
from netbox.views.generic import ObjectChangeLogView
from . import models, views

urlpatterns = [
    # Dashboard
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    
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

    # Pool Mappings
    path('pool-mappings/', views.PoolMappingListView.as_view(), name='poolmapping_list'),
    path('pool-mappings/add/', views.PoolMappingEditView.as_view(), name='poolmapping_add'),
    path('pool-mappings/<int:pk>/', views.PoolMappingView.as_view(), name='poolmapping'),
    path('pool-mappings/<int:pk>/edit/', views.PoolMappingEditView.as_view(), name='poolmapping_edit'),
    path('pool-mappings/<int:pk>/delete/', views.PoolMappingDeleteView.as_view(), name='poolmapping_delete'),
    path('pool-mappings/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='poolmapping_changelog', kwargs={'model': models.PoolMapping}),

    # LCA Impact Data
    path('lca-impact-data/', views.LCAImpactDataListView.as_view(), name='lcaimpactdata_list'),
    path('lca-impact-data/<int:pk>/', views.LCAImpactDataView.as_view(), name='lcaimpactdata'),
    path('lca-impact-data/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='lcaimpactdata_changelog', kwargs={'model': models.LCAImpactData}),

    # LCA Impact Indicator Values
    path('lca-impact-indicator-values/', views.LCAImpactIndicatorValueListView.as_view(), name='lcaimpactindicatorvalue_list'),
    path('lca-impact-indicator-values/<int:pk>/', views.LCAImpactIndicatorValueView.as_view(), name='lcaimpactindicatorvalue'),
    path('lca-impact-indicator-values/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='lcaimpactindicatorvalue_changelog', kwargs={'model': models.LCAImpactIndicatorValue}),

    # LCA Parameters
    path('lca-params/', views.LCAParamsView.as_view(), name='lcaparams_list'),
    path('lca-params/add/', views.LCAParamsEditView.as_view(), name='lcaparams_add'),
    path('lca-params/<int:pk>/', views.LCAParamsView.as_view(), name='lcaparams'),
    path('lca-params/<int:pk>/edit/', views.LCAParamsEditView.as_view(), name='lcaparams_edit'),
    path('lca-params/<int:pk>/delete/', views.LCAParamsDeleteView.as_view(), name='lcaparams_delete'),
    path('lca-params/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='lcaparams_changelog', kwargs={'model': models.LCAParams}),

    # Devices with ResilioDB info
    path('devices/', views.DeviceResilioListView.as_view(), name='device_list'),
    path('devices/sync/', views.DeviceBulkSyncView.as_view(), name='device_bulk_sync'),
]
