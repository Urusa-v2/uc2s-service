from accounts.models import User
from django.shortcuts import render, redirect
from django.db.models import Q
from django.db import connection


import os
import sys
import subprocess

# Create your views here.
def mainPage(request):
    return render(request, 'board/main.html')

def awsInputPage(request):
    if request.method == "GET":
        return render(request, 'board/aws_input.html')
    if request.method == "POST":
        aws_access_key_id = request.POST.get('aws_access_key_id',None)
        aws_secret_access_key = request.POST.get('aws_secret_access_key', None)
        if ( not aws_access_key_id) and (not aws_secret_access_key) :
            user = User.objects.get(id=request.user.id)
            user.aws_access_key_id = aws_access_key_id
            user.aws_secret_access_key = aws_secret_access_key
            user.save()
            context = {
              'aws_access_key_id': aws_access_key_id,
              'aws_secret_access_key': aws_secret_access_key
            }
            return render(request, 'board/aws_output.html', context)
        else :
            return redirect('/')


def deleteAwsKeyId(request):
    user = User.objects.get(id=request.user.id)
    user.aws_access_key_id = ''
    user.save()
    return redirect('/')

def deleteAwsSecretkey(request):
    user = User.objects.get(id=request.user.id)
    user.aws_secret_access_key = ''
    user.save()
    return redirect('/')


def githubInputPage(request):
    if request.method == "GET":
        return render(request, 'board/github_input.html')
    if request.method == "POST":
        github_access_token = request.POST.get('github_access_token', None)
        if( not github_access_token):
            user = User.objects.get(id=request.user.id)
            user.github_access_token = github_access_token
            user.save()

        #cursor = connection.cursor()
        #strsql = "SELECT id,username,github_access_token FROM accounts_user"
        #result = cursor.execute(strsql)
        #st = cursor.fetchall()
        #connection.commit()
        #connection.close()
        #print('st', st)


            context = {
                'github_access_token': github_access_token
            }
            return render(request, 'board/github_output.html',context)
        else :
            return redirect('/')

def deleteGitToken(request):
    user = User.objects.get(id=request.user.id)
    user.github_access_token = ''
    user.save()
    return redirect('/')


def getTokenPage(request):
    if request.method == "GET":
        aws_access_key_id = User.objects.filter(id=request.user.id).values('aws_access_key_id')
        aws_secret_access_key = User.objects.filter(id=request.user.id).values('aws_secret_access_key')
        github_access_token = User.objects.filter(id=request.user.id).values('github_access_token')
        print('aws',aws_access_key_id,aws_secret_access_key)

        #cursor = connection.cursor()
        #strsql = "SELECT * FROM accounts_user"
        #result = cursor.execute(strsql)
        #st = cursor.fetchall()
        #connection.commit()
        #connection.close()
        #print('st',st)

        context = {
            'aak': aws_access_key_id,
            'asa':aws_secret_access_key,
            'gat':github_access_token
        }
        return render(request, 'board/token_output.html',context)

def startcicd(request):
    if request.method == "GET":
        return render(request, 'board/startcicd.html')
    if request.method == "POST":
        githubrepo_address = request.POST.get('githubrepo_address', None)
        if( not githubrepo_address) :
            #서브 프로세스로 shell 실행 -> ssh 로 젠킨스 노드에 명령 전달
            print( githubrepo_address)

            # key 가져오기
            aws_access_key_id = "asdasd"
            aws_secret_access_key = "asdadasd"
            github_access_token = "asdasdsad"

            # shell 을 통해 jenkins 에 데이터 전달 및 실행
            subprocess.Popen(['setjenkins.sh %s %s %s %s'%(githubrepo_address,aws_access_key_id,aws_secret_access_key,github_access_token)],shell=True)
            context = {
                'githubrepo_address': githubrepo_address
            }
            return render(request, 'board/githubrepo_output.html',context)

        else :
            return redirect('/')