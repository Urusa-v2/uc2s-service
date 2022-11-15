from .forms import SignupForm
from .models import User
from django.shortcuts import render
from django.contrib.auth.forms import AuthenticationForm

from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login, logout as auth_logout # 함수이름과 겹치지않기 위해 수정


# 회원가입
def singup(request):
    if request.method == "GET":
        signupForm = SignupForm()
        return render(request,'accounts/signup.html', {'signupForm':signupForm})
    elif request.method == "POST":
        signupForm = SignupForm(request.POST)
        if signupForm.is_valid():
            user = signupForm.save(commit=False)
            user.save()

        return redirect('/')

# 로그인 입력 양식이 주어져야함
def login(request):
    if request.method == "GET":
        loginForm = AuthenticationForm()
        return render(request,'accounts/login.html', {'loginForm' : loginForm})
    elif request.method == "POST":
        loginForm = AuthenticationForm(request, request.POST)
        if loginForm.is_valid():
            auth_login(request, loginForm.get_user())
            return redirect('/')

def logout(request):
    # 세션 정보를 지우는 것
    auth_logout(request)
    return redirect('/')

def signout(request):
    user = User.objects.get(id=request.user.id)
    user.delete()
    return redirect('/')