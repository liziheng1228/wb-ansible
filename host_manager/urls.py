from django.urls import path
from .views import HostCreateView, HostUpdateView, HostDeleteView
from . import views

# app_name = 'host_manager'
urlpatterns = [
    path('', views.go_host_manager, name='go_host_manager'),
    path('create/', HostCreateView.as_view(), name='host_create'),
    path('update/<int:pk>/', HostUpdateView.as_view(), name='host_update'),
    path('delete/<int:pk>/', HostDeleteView.as_view(), name='host_delete'),

    # API
    path('api/hosts/batch-delete/', views.batch_delete, name='batch_delete_host_api'),
    path('api/hosts/host-list//', views.get_hosts_list_api, name='get_host_list_api'),

]
