from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .utils import generate_otp, send_otp_email
from django.utils import timezone
from .models import User, FriendRequest, Friendship
from django.shortcuts import render, get_object_or_404

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

def Home(request):
    return render(request, 'home.html')

def UserProfile(request, username):
    user = get_object_or_404(User, username=username)
    bio = request.user.Bio if request.user.Bio else ''
    return render(request, 'userprofile.html', {'user':user,'bio': bio})

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

def SearchOtherUsers(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        if username:
            try:
                searched_user = User.objects.get(username=username)
                return render(request, 'searchpeople.html', {'searched_user':searched_user})
            except User.DoesNotExist:
                error_messege = "User Does not Exist."
                return render(request, 'searchpeople.html', {'error_messege':error_messege})
        else:
            error_messege = "Please enter a valid Username"
            return render(request, 'searchpeople.html', {'error_messege':error_messege})
    else:
        return render(request, 'searchpeople.html')
    
def OtherUserProfile(request, username):
    searched_user = get_object_or_404(User, username=username)
    bio = searched_user.Bio if searched_user.Bio else ''
    followers_count = 500  # Replace with actual follower count
    following_count = 200  # Replace with actual following count
    friend_request_sent = FriendRequest.objects.filter(from_user=request.user, to_user=searched_user).exists()
    return render(request, 'otheruserprofile.html', {'searched_user': searched_user, 'bio': bio, 'followers_count': followers_count, 'following_count': following_count, 'friend_request_sent': friend_request_sent})

def send_friend_request(request,username):
    if request.method == 'POST':
        from_user = request.user
        print(from_user)
        to_user = get_object_or_404(User, username=username)
        friend_request = FriendRequest(from_user=from_user, to_user=to_user)
        friend_request.save()
        messages.info(request, "Send Friend Request")
        return redirect('other-profile', username=username)
    return redirect('home')

def accept_friend_request(request, username):
    friend_request = get_object_or_404(FriendRequest, to_user = request.user , from_user_username = username)
    Friendship.objects.create(user1 =  friend_request.from_user , user2 = friend_request.to_user)
    friend_request.delete()
    messages.add_message('Accept request successfully')
    # return redirect('friendsList')

def reject_friend_request(request, username):
    friend_request = get_object_or_404(FriendRequest, to_user = request.user , from_user_username = username)
    friend_request.delete()
    return redirect('friendsList')

def friendsList(request):
    friends = Friendship.objects.filter(user1=request.user) | Friendship.objects.filter(user2=request.user)
    return render(request, 'friendslist.html', {'friends':friends})