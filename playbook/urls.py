from django.urls import path

from . import views
from .views import PlaybookDeleteView

# edit_code
urlpatterns = [

    # 页面跳转部分（返回 HTML 页面）
    path('list/', views.playbook_list_page, name='list_page'),
    path('editcode/', views.edit_code_page, name='edit_code'),
    path('<str:playbook_id>/', views.playbook_detail_page, name='detail_page'),
    path('update/<int:pk>/', views.PlaybookUpdateView.as_view(), name='playbook_update'),

    #API 部分 ajax获取
    path('delete/<int:pk>/', PlaybookDeleteView.as_view(), name='host_delete'),
    path('api/playbook/batch-delete/', views.batch_delete, name='batch_delete_playbook_api'),
    path('api/save_code', views.save_code, name='save_code'),
    path('api/playbook/list/', views.get_playbook_list_api, name='get_playbook_list_api'),
    path('api/playbook/<str:playbook_id>/', views.get_playbook_detail_api, name='api_detail'),

]
