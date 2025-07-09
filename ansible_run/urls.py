from django.urls import path

from . import views

urlpatterns = [

    path("", views.go_index, name="go_index"),
    path("go_result_page/<str:task_id>/", views.go_result_page, name="go_result_page"),
    path('go_task_list/', views.go_task_list, name='go_task_list'),
    path('get_csrf_token/', views.get_csrf_token, name='get_csrf_token'),
    path('get_result/<str:task_id>/', views.get_result, name='get_result'),

    # api
    path('api/get_task_list', views.get_task_list_api, name='get_task_list_api'),
    path('api/ansible_run', views.ansible_run, name='ansible_run'),

]
