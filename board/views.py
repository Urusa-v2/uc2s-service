from django.shortcuts import render, redirect
from django.db.models import Q
from django.db import connection
from board.models import Token

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
        token = Token.objects.get(user = request.user)
        token.user = request.user
        token.aws_access_key_id = request.POST.get('aws_access_key_id',None)
        token.aws_secret_access_key = request.POST.get('aws_secret_access_key', None)
        if ( token.aws_access_key_id != "" ) and (token.aws_secret_access_key != "") :
            token.save()
            context = {
              'aws_access_key_id': token.aws_access_key_id,
              'aws_secret_access_key': token.aws_secret_access_key
            }
            return render(request, 'board/aws_output.html', context)
        else :
            return redirect('/')


def deleteAwsKeyId(request):
    token = Token.objects.get(user = request.user)
    token.aws_access_key_id = ''
    token.save()
    return redirect('/')

def deleteAwsSecretkey(request):
    token = Token.objects.get(user = request.user)
    token.aws_secret_access_key = ''
    token.save()
    return redirect('/')


def githubInputPage(request):
    if request.method == "GET":
        return render(request, 'board/github_input.html')
    if request.method == "POST":
        token = Token.objects.get(user = request.user)
        token.github_access_token = request.POST.get('github_access_token', None)
        if( token.github_access_token != "" ):
            token.user = request.user
            token.save()

            context = {
                'github_access_token': token.github_access_token
            }
            return render(request, 'board/github_output.html',context)
        else :
            return redirect('/')

def deleteGitToken(request):
    token = Token.objects.get(user_id=request.user.id)
    token.github_access_token = ''
    token.save()
    return redirect('/')


def getTokenPage(request):
    if request.method == "GET":
        aws_access_key_id = Token.objects.filter(user_id=request.user.id).values('aws_access_key_id')
        aws_secret_access_key = Token.objects.filter(user_id=request.user.id).values('aws_secret_access_key')
        github_access_token = Token.objects.filter(user_id=request.user.id).values('github_access_token')
        print('aws',aws_access_key_id,aws_secret_access_key)

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
            print( githubrepo_address)

            # key 가져오기
            aws_access_key_id = Token.objects.filter(user_id=request.user.id).values('aws_access_key_id')
            aws_secret_access_key = Token.objects.filter(user_id=request.user.id).values('aws_secret_access_key')
            github_access_token = Token.objects.filter(user_id=request.user.id).values('github_access_token')

            # shell 을 통해 jenkins 에 데이터 전달 및 실행
            subprocess.Popen(['setjenkins.sh %s %s %s %s'%(githubrepo_address,aws_access_key_id,aws_secret_access_key,github_access_token)],shell=True)
            context = {
                'githubrepo_address': githubrepo_address
            }
            return render(request, 'board/githubrepo_output.html',context)

        else :
            return redirect('/')