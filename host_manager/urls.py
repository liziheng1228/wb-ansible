from django.urls import path
from .views import HostListView, HostCreateView, HostUpdateView, HostDeleteView

# app_name = 'host_manager'
urlpatterns = [
    path('', HostListView.as_view(), name='host_list'),
    path('create/', HostCreateView.as_view(), name='host_create'),
    path('update/<int:pk>/', HostUpdateView.as_view(), name='host_update'),
    path('delete/<int:pk>/', HostDeleteView.as_view(), name='host_delete'),
]
