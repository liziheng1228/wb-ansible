from django.urls import path, include
from django.contrib import admin
from . import views
from django.contrib.auth import views as auth_views
urlpatterns = [
    path("register/", views.register, name="register"),
    path("", views.login, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("forget_password/", views.forget_password, name="forget_password"),
    path('reset-password/', views.MyPasswordResetView.as_view(), name='password_reset'),
    path('reset-password/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset-password/confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(success_url='/'),
         name='password_reset_confirm'),
    path('reset-password/complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
