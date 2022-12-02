from .forms import SignupForm
from .forms import LeaderSignupForm
from .forms import groupForm
from .models import User
from .models import Groups
from board.models import Token
from django.shortcuts import render
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required

from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login, logout as auth_logout # 함수이름과 겹치지않기 위해 수정

from django.db import connection

import os
import sys
import subprocess
from django.contrib import messages

# 회원가입시 일반 유저인지 리더인지 선택
def chooseuser(request):
    return render(request,'accounts/setsignupuser.html')

# 팀원 개발자 회원가입
def singup(request):
    if request.method == "GET":
        signupForm = SignupForm()
        grouplist=Groups.objects.all()
        return render(request,'accounts/signup_user.html', {'signupForm':signupForm, 'grouplist':grouplist})
    elif request.method == "POST":
        signupForm = SignupForm(request.POST)
        print(signupForm)
        if signupForm.is_valid():
            user = signupForm.save(commit=False)
            user.isleader=False
            user.save()
            return redirect('/accounts/login')
        else:
            messages.info(request, 'Account creation failed. Check your form! ')
            signupForm = SignupForm()
            grouplist = Groups.objects.all()
            return render(request, 'accounts/signup_user.html', {'signupForm': signupForm, 'grouplist': grouplist})

# 그룹 생성하기
def createGroup(request):
    if request.method == "GET":
        groupform = groupForm()
        return render(request,'accounts/creategroup.html', {'groupForm':groupform})
    elif request.method =="POST":
        groupform = groupForm(request.POST)
        if groupform.is_valid():
            group = groupform.save(commit=False)
            group.save()
            return redirect('/accounts/leadersingup/' + str(group.id))
        else:
            messages.info(request, 'This group is already created. ')
            groupform = groupForm()
            return render(request, 'accounts/creategroup.html', {'groupForm': groupform})

# 그룹장 회원가입
def leadersingup(request, bid):
    if request.method == "GET":
        signupForm = LeaderSignupForm()
        return render(request,'accounts/signup_leader.html', {'signupForm':LeaderSignupForm})
    elif request.method == "POST":
        signupForm = LeaderSignupForm(request.POST)
        if signupForm.is_valid():
            user = signupForm.save(commit=False)
            user.isleader = True
            group = Groups.objects.get(id=bid)
            user.group = group
            user.save()
            
            # Jenkins 계정의 ID 는 GROUP 의 이름으로 지정한다
            groupname = group.name

            # 해당 SHELL 은 jenkins 유저 생성 명령 및 api 토큰 생성 명령 실행을 내리고, PIPE 를 통해 결과를 반환한다
            result = subprocess.Popen(['/var/www/django/accounts/setjenkinsuser.sh %s' % (groupname)],
                                      shell=True, stdout=subprocess.PIPE)
            
            # 실행 결과인 TOKEN 값만을 저장
            jenkinstoken = result.communicate()[0]
            # 반환 결과는 바이트 표현이 붙은 ascii 형식의 바이트 코드이다. 이를 복호화하여 유니코드 문자열로 변환한다
            jenkinstoken = jenkinstoken.decode('ascii')
            # 해당 유저의 TOKEN TABLE 생성 ( 생성자 )
            token = Token()
            # 어떤 그룹의 토큰인지 설정
            token.group = group
            token.jenkins_access_token = jenkinstoken
            token.save()

            # 토큰 입력 페이지로 넘어가면, 회원 가입한 유저의 그룹의 토큰을 입력받는다. 따라서 토큰의 id 를 넘겨서 해당 table 에 입력받게 한다
            return redirect('/accounts/inputtoken/' + str(token.id))
        else:
            # 입력한 값이 잘못됬을 경우 처리
            messages.info(request, 'Account creation failed. Check your form! ')
            signupForm = LeaderSignupForm()
            return render(request, 'accounts/signup_leader.html', {'signupForm': LeaderSignupForm})

# 그룹장의 토큰 입력 기능
def TokenInputPage(request, bid):
    if request.method == "GET":
        return render(request, 'accounts/token_input.html')
    if request.method == "POST":
        token = Token.objects.get(id=bid)
        token.aws_access_key_id = request.POST.get('aws_access_key_id',None)
        token.aws_secret_access_key = request.POST.get('aws_secret_access_key', None)
        if ( token.aws_access_key_id != "" ) and (token.aws_secret_access_key != ""):
            token.save()
            context = {
              'aws_access_key_id': token.aws_access_key_id,
              'aws_secret_access_key': token.aws_secret_access_key,
            }
            return render(request, 'accounts/token_confirm.html', context)
        else :
            signupForm = LeaderSignupForm()
            return render(request, 'accounts/signup_leader.html', {'signupForm': LeaderSignupForm})

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
        else:
            messages.info(request, 'Login failed. Check your form! ')
            return redirect('/accounts/login')

@login_required(login_url='/accounts/login')
def logout(request):
    # 세션 정보를 지우는 것
    auth_logout(request)
    return redirect('/')

@login_required(login_url='/accounts/login')
def withdraw(request):
    user=User.objects.get(id=request.user.id)
    user.delete()
    return redirect('/')


@login_required(login_url='/accounts/login')
def profile(request):
    # user 정보 조회
    user = User.objects.get(id=request.user.id)

    # token 정보 조회
    aws_access_key_id = Token.objects.filter(group=request.user.group).values('aws_access_key_id')
    aws_secret_access_key = Token.objects.filter(group=request.user.group).values('aws_secret_access_key')

    context = {'userlist': user, 'aak': aws_access_key_id,
               'asa': aws_secret_access_key,
               }
    if request.method=="GET":
        return render(request, 'accounts/profile.html', context)
    elif request.method=="POST":
        token = Token.objects.get(group=request.user.group)
        token.aws_access_key_id = request.POST.get('aws_access_key_id',None)
        token.aws_secret_access_key = request.POST.get('aws_secret_access_key',None)
        token.save()

        return render(request,'accounts/profile.html',context)
