from django.urls import path

from netbox.views.generic import ObjectChangeLogView
from . import models, views

urlpatterns = [
    path('lca/', views.LCAListView.as_view(), name='lca_list'),
    path('lca/changelog/', ObjectChangeLogView.as_view(), name='lca_changelog', kwargs={'model': models.LCAData}),
]
