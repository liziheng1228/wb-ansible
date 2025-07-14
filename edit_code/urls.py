from django.urls import path

from . import views
# edit_code
urlpatterns = [
    path('', views.edit_code_index, name='edit_code_index'),
    path('api/save_code', views.save_code, name='save_code'),
]
