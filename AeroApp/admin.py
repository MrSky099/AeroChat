from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, FriendRequest, Friendship

class Useradmin(UserAdmin):
    model = User
    list_display = ['email','full_name','username','Bio', 'is_staff', 'date_joined']

class FriendRequestAdmin(admin.ModelAdmin):
    model = FriendRequest
    list_display = ['from_user', 'to_user', 'created_at']

class FriendshipAdmin(admin.ModelAdmin):
    model = Friendship
    list_display = ['user1', 'user2', 'created_at']

admin.site.register(User,Useradmin)
admin.site.register(FriendRequest,FriendRequestAdmin)
admin.site.register(Friendship,FriendshipAdmin)