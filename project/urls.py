"""
URL configuration for project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', include(('userlogin.urls','login'), namespace='login')),
    path('scripts/',include(('scripts.urls','playbook'),namespace='scripts'),name='scripts'),
    path('', include(('ansible_run.urls', 'ansible_run'),namespace='ansible_run'), name='ansible_run'),
    path('runner_jobs/', include(('runner_jobs.urls', 'runner_jobs'),namespace='runner_jobs')),
    path('host_manager/', include(('host_manager.urls', 'host_manager'),namespace='host_manager'), name='host_manager'),

]
