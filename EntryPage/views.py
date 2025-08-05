import datetime

from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from .models import Profile
from .forms import RegisterForm


# Create your views here.

def hello(request , number):
    # text = "<h1>hello</h1>"
    # return HttpResponse(text)
    # today = datetime.datetime.today()
    # return render(request, 'hello.html', {"today": today})
    height = request.GET["height"]
    # return render(request, 'hello.html',{'data':height, 'data2':60})
    return render(request, 'hello.html',{'data':height, 'data2':number})

def entry_view(request):

    if request.user.is_authenticated:
        profile = Profile.objects.get(user=request.user)
        if profile.role == 'user':
            return redirect('/user/dashboard/')
        else:
            return redirect('/owner/dashboard/')
    return redirect('/EntryPage/login_view/')

from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import RegisterForm
from captcha.models import CaptchaStore
from captcha.helpers import captcha_image_url

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        # 產生一組新的驗證碼
        new_key = CaptchaStore.generate_key()
        image_url = captcha_image_url(new_key)
        context = {
        'form': form,
        'captcha_key': new_key,
        'captcha_image_url': image_url,
        }


        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password1']
            role = form.cleaned_data['role']
            # 建立使用者帳號
            if User.objects.filter(username=username).exists():
                messages.error(request, "此帳號已被註冊")
            else:
                user=User.objects.create_user(username=username, email=email, password=password)
                user.profile.role = role
                user.profile.save()
                send_verification_email(user)
                return render(request, 'message.html', {'msg': '註冊成功，請至信箱點擊驗證連結'})
        else:
            messages.error(request, "請確認表單填寫正確")
    else:
        form = RegisterForm()
        new_key = CaptchaStore.generate_key()
        image_url = captcha_image_url(new_key)
    return render(request, 'register.html', {
        'form': form,
        'captcha_key': new_key,
        'captcha_image_url': image_url
    })

def send_verification_email(user):
    token = user.profile.verification_token
    url = f"http://127.0.0.1:8000/EntryPage/verify-email/{token}/"  #正式網域要記得換
    # url = f"parking-space-06b78525c978.herokuapp.com/EntryPage/verify-email/{token}/"  #正式網域要記得換
    subject = "請驗證你的帳號"
    message = f"請點擊以下連結驗證帳號：\n\n{url}"
    print("已寄送EMAIL")
    send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email])

def verify_email_view(request, token):
    try:
        profile = Profile.objects.get(verification_token=token)
        profile.is_email_verified = True
        profile.save()
        return render(request, 'message.html', {'msg': '信箱驗證成功，請返回登入頁面'})
    except Profile.DoesNotExist:
        return render(request, 'message.html', {'msg': '驗證失敗，連結無效'})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            if not user.profile.is_email_verified:
                return render(request, 'login.html', {'error': '請先完成信箱驗證'})
            login(request, user)
            if request.user.profile.role == 'owner':
                return redirect('/OwnerInterface/owner_dashboard/')
            else:
                return redirect('/UserInterface/dashboard/')
        else:
            return render(request, 'login.html', {'error': '帳號或密碼錯誤'})
    return render(request, 'login.html')
