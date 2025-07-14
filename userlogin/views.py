from django.contrib.auth import authenticate,logout
from django.contrib.auth import login as django_login
from django.contrib.auth.hashers import check_password
from django.db import IntegrityError
from django.shortcuts import render, redirect
# from django.contrib.auth.models import User
# from userlogin.forms import EmailForm
from .models import User
from django.contrib.auth.views import PasswordResetView

# Create your views here.

class MyPasswordResetView(PasswordResetView):
    template_name = "emailfrom/index.html"




def register(request):
    error = None
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        email = request.POST.get("email")
        try:
            User.objects.create_user(
                username=username,
                password=password,
                email=email
            )
            return redirect('/')  # 成功跳转
        except IntegrityError:
            email_exists = User.objects.filter(email=email).exists()
            username_exists = User.objects.filter(username=username).exists()
            if email_exists and username_exists:
                error = "用户和邮箱已被使用"
            elif username_exists:
                error = "用户名已被使用"
            elif email_exists:
                error = "邮箱已被使用"
            # error_key = str(e).split("'")[1]

            return render(request, "register/index.html", {'error': error})
        #
        # if User.objects.filter(email=email).exists():
        #     error = "账号或邮箱已使用"
        # else:
        #     User.objects.create_user(username=username, password=password, email=email)
        #     return redirect('/')  # 成功跳转
    return render(request, "register/index.html", {'error': error})


# 忘记密码
def forget_password(request):
    if request.method == "POST":
        # old_password = request.POST.get("old_password")
        username = request.POST.get("username")
        new_password = request.POST.get("new_password")
        if User.objects.filter(username=username).exists():
            request.user.set_password(new_password)
            request.user.save()
        else:
            error = "账号不存在"
            return render(request, "forget_password/index.html", {'error': error})

    return render(request, "forget_password/index.html")


# 登录
def login(request):
    error = None
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user  = authenticate(request,username=username,password=password)
        if user is not None:
            # 页面保存session登录信息
            django_login(request, user)

            # return render(request, "runner_jobs/job_detail.html")
            # 跳转到首页
            return redirect('ansible_run:go_index')
        else:
            error = "账号或密码错误"
            print(error)
            return render(request,"login/index.html",context={'error':error})
    return render(request, "login/index.html")


def logout_view(request):
    logout(request)
    return render(request, "login/index.html")