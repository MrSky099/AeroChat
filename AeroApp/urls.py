from django.contrib import admin
from django.urls import path
from AeroApp import views

urlpatterns = [
    path('register/', views.UserRegistration , name ='register'),
    path('login/', views.UserLogin , name = 'login'),
    path('verify-otp/', views.UserOTPVerify, name ='verify-otp'),
    path('home/', views.Home , name ='home'),
    path('profile/', views.UserProfile, name='profile'),
    path('bio/', views.UserBio, name='bio'),
    path('logout/', views.UserLogout, name='logout'),
]