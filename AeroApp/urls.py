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
    path('<str:username>/', views.OtherUserProfile, name='other-profile'),

]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)