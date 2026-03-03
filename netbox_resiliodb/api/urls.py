from netbox.api.routers import NetBoxRouter

from . import views

app_name = "netbox_resiliodb"

router = NetBoxRouter()
router.register("lca-types", views.LCATypeViewSet)
router.register("indicators", views.IndicatorViewSet)
router.register("device-role-lca-mappings", views.DeviceRoleLCATypeMappingViewSet)
router.register("site-country-mappings", views.SiteCountryMappingViewSet)
router.register("lca-params", views.LCAParamsViewSet)
router.register("plugin-settings", views.PluginSettingsViewSet)
router.register("device-sync", views.DeviceSyncViewSet, basename="device-sync")
router.register("lca-impact-data", views.LCAImpactDataViewSet)
router.register("lca-impact-indicator-values", views.LCAImpactIndicatorValueViewSet)
router.register("pool-mappings", views.PoolMappingViewSet)

urlpatterns = router.urls
