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
    path('chat/', views.Chat, name='chat'),

    path('profile/<str:username>/', views.UserProfile, name='profile'),
    path('home/', views.Home , name ='home'),
    path('send-friend-request/<str:username>/', views.send_friend_request, name='send-friend-request'),
    path('accept-friend-request/<int:request_id>/', views.accept_friend_request, name='accept-friend-request'),
    path('accept-friend-request-for-particularPerson/<int:request_id>/', views.accept_friend_request_for_particularPerson, name='accept-friend-request-for-particularPerson'),
    path('reject-friend-request/<int:request_id>/', views.reject_friend_request, name='reject-friend-request'),
    path('reject-friend-request-from-sender/<int:request_id>/', views.reject_friend_request_from_sender_user, name='reject-friend-request-from-sender'),
    path('friends/', views.friendsList, name='friends'),
    path('requests/', views.PandingRequest , name='requests'),
    path('<str:username>/', views.OtherUserProfile, name='other-profile'),

]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)