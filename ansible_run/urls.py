from django.urls import path, include
from django.contrib import admin
from . import views

urlpatterns = [


    path('trigger-task/', views.trigger_task, name='trigger_task'),
    path("", views.ansible_run_index, name="ansible_run_index"),
    path("go_result_page/<str:task_id>/", views.go_result_page, name="go_result_page"),
    path('get_csrf_token/', views.get_csrf_token, name='get_csrf_token'),


    path('get_result/<str:task_id>/', views.get_result, name='get_result'),

    path('get_task_id/', views.get_task_id, name='get_task_id'),


    # api
    path('api/get_task_list', views.get_task_list_api, name='get_task_list_api'),


]
