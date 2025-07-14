from django.contrib import admin

from userlogin.models import User

# # Register your models here.
# admin.site.register(User)

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'is_staff', 'is_superuser', 'is_active')