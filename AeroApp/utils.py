import random
from django.core.mail import send_mail
import threading

def generate_otp():
    return str(random.randint(111111,999999))

def send_otp_email(email,otp):
    subject = 'Your OTP for AeroChat Login'
    message = f'your OTP is {otp}'
    from_email = 'akashpatel1602906@gmail.com'
    recipient_list = [email]
    threading.Thread(target=send_mail, args=(subject,message,from_email, recipient_list)).start()
    # send_mail(subject, message, from_email, recipient_list)