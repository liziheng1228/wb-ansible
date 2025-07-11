from django.urls import path
from django.urls import path
from .views import job_list, job_create, job_delete, go_jobs, job_detail,get_hosts
# runner_jobs
# app_name = 'host_manager'
urlpatterns = [
    path('', go_jobs, name='go_jobs'),
    path('jobs/<uuid:job_id>/', job_detail, name='job-detail'),
    path('api/jobs/', job_list, name='job-list'),
    path('api/jobs/create/', job_create, name='job-create'),
    path('api/jobs/delete/<uuid:job_id>/', job_delete, name='job-delete'),
    path('api/hosts/', get_hosts, name='get-hosts'),
]
