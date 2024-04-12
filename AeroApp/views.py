from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .utils import generate_otp, send_otp_email
from django.utils import timezone
from .models import User, FriendRequest, Friendship
from django.shortcuts import render, get_object_or_404
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required

User = get_user_model()

def UserRegistration(request):
    #user registration
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

        user = User.objects.filter(username=username).first()

        if not user:
            messages.error(request, 'Invalid Username')
            return redirect('login')     
           
        authenticated_user = authenticate(username=username, password=password)

        if authenticated_user is not None:
            otp = generate_otp()
            print(otp)
            send_otp_email(user.email, otp)
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
                request.session.pop('username', None)
                request.session.pop('otp_time', None)
                request.session.pop('otp', None)
                messages.error(request,'OTP Expired. Please request a new one.')
                return redirect('verify-otp')
        
        if otp_entered == otp_send:
            user = User.objects.get(username=username)
            login(request,user)
            request.session.pop('username', None)
            request.session.pop('otp', None)
            return redirect('home')
        else:
            messages.error(request, 'Invalid OTP')
            return redirect('verify-otp')
        
    return render(request, 'verify-otp.html')
def UserLogout(request):
    logout(request)
    return redirect('register')

@login_required
def Home(request):
    return render(request, 'home.html')

@login_required
def UserProfile(request, username):
    user = get_object_or_404(User, username=username)
    bio = request.user.Bio if request.user.Bio else ''
    friendship1 = Friendship.objects.filter(user1=request.user).count()
    friendship2 = Friendship.objects.filter(user2=request.user).count()
    total_frineds = friendship1 + friendship2
    return render(request, 'userprofile.html', {'user':user,'bio': bio, 'total_frineds':total_frineds})

@login_required
def UserBio(request):
    if request.method == 'POST':
        user = request.user
        Bio = request.POST.get('Bio')
        user.Bio = Bio
        user.save()
        bio = user.Bio
        return redirect('profile', username=user.username)
    bio = request.user.Bio if request.user.Bio else ''
    return render(request, 'bio.html', {'bio': bio})

@login_required
def SearchOtherUsers(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        if username:
            current_user = request.user
            if username != current_user.username:
                try:
                    searched_user = User.objects.get(username=username)
                    return render(request, 'searchpeople.html', {'searched_user':searched_user})
                except User.DoesNotExist:
                    error_messege = "User Does not Exist."
                    return render(request, 'searchpeople.html', {'error_messege':error_messege})
            else:
                error_message = "You cannot search for yourself."
                return render(request, 'searchpeople.html', {'error_message':error_message})
        else:
            error_messege = "Please enter a valid Username"
            return render(request, 'searchpeople.html', {'error_messege':error_messege})
    else:
        return render(request, 'searchpeople.html')

@login_required   
def OtherUserProfile(request, username):
    searched_user = get_object_or_404(User, username=username)
    bio = searched_user.Bio if searched_user.Bio else ''
    friend_request_sent = FriendRequest.objects.filter(from_user=request.user, to_user=searched_user).first()
    friend_request = FriendRequest.objects.filter(to_user=request.user)
    return render(request, 'otheruserprofile.html', {'searched_user': searched_user, 'bio': bio, 'friend_request_sent': friend_request_sent, 'friend_request': friend_request})

@login_required
def send_friend_request(request,username):
    if request.method == 'POST':
        if Friendship.objects.filter(user1=request.user, user2=request.user).exists():
            messages.info(request, 'Friendship already exists')
        from_user = request.user
        to_user = get_object_or_404(User, username=username)
        existing_request = FriendRequest.objects.filter(from_user=from_user, to_user=to_user).exists()
        if not existing_request:
            friend_request = FriendRequest(from_user=from_user, to_user=to_user)
            friend_request.save()
            messages.info(request, "Send Friend Request")
            return redirect('other-profile', username=username)
    return render(request, 'otheruserprofile.html')

@login_required
def accept_friend_request(request, request_id):
    if request.method == 'POST':
        friend_request = get_object_or_404(FriendRequest, id=request_id)
        user1 = friend_request.from_user
        user2 = friend_request.to_user

        if Friendship.objects.filter(user1=user1, user2=user2).exists():
            messages.info(request, 'Friendship already exists')
            return redirect('requests')
        
        if Friendship.objects.filter(user1=user2, user2=user1).exists():
            messages.info(request, 'Friendship already exists')
            return redirect('requests')
        try:
            Friendship.objects.create(user1=user1, user2=user2)
            friend_request.delete()
            messages.info(request, 'Friend request accepted successfully')
            return redirect('requests')
        except IntegrityError:
            messages.error(request, 'Error')
            return redirect('requests')
    return render(request, 'pending_request.html', {'friend_request':friend_request})

@login_required
def reject_friend_request(request, request_id):
    if request.method == 'POST':
        friend_request = get_object_or_404(FriendRequest, id=request_id)
        friend_request.delete()
        messages.info(request,'Reject request successfully')
        return redirect('requests')
    return render(request, 'pending_request.html', {'friend_request':friend_request})

@login_required
def reject_friend_request_from_sender_user(request,request_id):
    if request.method == 'POST':
        friend_request = get_object_or_404(FriendRequest, id=request_id, from_user = request.user)
        friend_request.delete()
        messages.info(request,'Reject request successfully')
        return redirect('other-profile', username=friend_request.to_user.username)
    return render(request, 'otheruserprofile.html', {'friend_request':friend_request})

@login_required
def friendsList(request):
    if not Friendship.objects.filter(user1=request.user, user2=request.user).exists():
        friendship1 = Friendship.objects.filter(user1=request.user)
        friendship2 = Friendship.objects.filter(user2=request.user)
        friend1 = [i.user2 for i in friendship1]
        friend2  =[i.user1 for i in friendship2]
        Friends = friend1 + friend2
        return render(request, 'showfriend.html', {'Friends':Friends})

@login_required
def PandingRequest(request):
    friend_requests = FriendRequest.objects.filter(to_user=request.user)
    friend_requests_dict = {'friend_requests': list(friend_requests)}
    return render(request, 'pending_request.html', friend_requests_dict)