from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role')  # Ensure these fields are displayed


    

admin.site.register(User, CustomUserAdmin)
