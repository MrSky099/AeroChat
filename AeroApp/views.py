from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .utils import generate_otp, send_otp_email
from django.utils import timezone

User = get_user_model()

def UserRegistration(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        full_name = request.POST.get('full_name')
        username = request.POST.get('username')
        password = request.POST.get('password')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already taken.")
            return render(request, 'register.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return render(request, 'register.html')

        user = User.objects.create_user(
            email=email, 
            username=username,
            password=password
        )
        user.full_name = full_name
        user.set_password(password)
        user.save()
        messages.info(request, "Account created Successfully!")
        return redirect('login')
    
    return render(request, 'register.html')

def UserLogin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not User.objects.filter(username=username).exists():
            messages.error(request,'Invalid Username')
            return redirect('login')
        
        user = authenticate(username=username, password=password)

        if user is not None:
            otp = generate_otp()
            send_otp_email(user.email,otp)
            request.session['otp'] = otp
            request.session['username'] = username
            request.session['otp_time'] = timezone.now().isoformat()
            return redirect('verify-otp')
        else:
            messages.error(request,'Invalid password')
            return redirect('login')
    return render(request, 'login.html')

def UserOTPVerify(request):
    if request.method == 'POST':
        otp_entered = request.POST.get('otp')
        otp_send = request.session.get('otp')
        username = request.session.get('username')
        otp_time_str = request.session.get('otp_time')

        otp_time = timezone.datetime.fromisoformat(otp_time_str) if otp_time_str else None

        if otp_time:
            time_difference = timezone.now() - otp_time
            if time_difference.total_seconds() > 300:
                del request.session['username']
                del request.session['otp_time']
                del request.session['otp']
                messages.error(request,'OTP Expired. Please request a new one.')
                return redirect('verify-otp')
        
        if otp_entered == otp_send:
            user = User.objects.get(username=username)
            login(request,user)
            del request.session['otp']
            del request.session['username']
            return redirect('home')
        else:
            messages.error(request, 'Invalid OTP')
            return redirect('verify-otp')
        
    return render(request, 'verify-otp.html')

def Home(request):
    return render(request, 'home.html')

def UserProfile(request):
    return render(request,'userprofile.html')
        
        