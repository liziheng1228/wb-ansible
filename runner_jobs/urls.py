
from django.urls import path
from . import views

# runner_jobs
# app_name = 'runner_jobs'
urlpatterns = [
    path('', views.go_jobs, name='go_jobs'),
    path('jobs/<uuid:job_id>/', views.job_detail, name='job-detail'),



    path('api/jobs/batch-delete/', views.batch_delete, name='batch_delete_jobs_api'),
    path('api/jobs/', views.job_list, name='job-list'),
    path('api/jobs/create/', views.job_create, name='job-create'),
    path('api/jobs/delete/<uuid:job_id>/', views.job_delete, name='job-delete'),
    path('api/hosts/', views.get_hosts, name='get-hosts'),
]
