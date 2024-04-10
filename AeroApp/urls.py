from django.contrib import admin
from django.urls import path
from AeroApp import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('register/', views.UserRegistration , name ='register'),
    path('login/', views.UserLogin , name = 'login'),
    path('verify-otp/', views.UserOTPVerify, name ='verify-otp'),
    path('logout/', views.UserLogout, name='logout'),
    path('bio/', views.UserBio, name='bio'),
    path('search/', views.SearchOtherUsers, name = 'search'),

    path('profile/<str:username>/', views.UserProfile, name='profile'),
    path('home/', views.Home , name ='home'),
    path('send-friend-request/<str:username>/', views.send_friend_request, name='send_friend_request'),
    path('accept-friend-request/<int:request_id>/', views.accept_friend_request, name='accept-friend-request'),
    path('reject-friend-request/<str:username>/', views.reject_friend_request, name='reject_friend_request'),
    path('friends/', views.friendsList, name='friendsList'),
    path('requests/', views.PandingRequest , name='requests'),
    path('<str:username>/', views.OtherUserProfile, name='other-profile'),

]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)