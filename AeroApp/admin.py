from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class Useradmin(UserAdmin):
    model = User
    list_display = ['email','full_name','username', 'is_staff', 'date_joined']

admin.site.register(User,Useradmin)