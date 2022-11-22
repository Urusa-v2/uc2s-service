from django.shortcuts import render, redirect
from django.db.models import Q
from django.db import connection

from api.ecr_inform import getRepoDescription, getRepoName
from api.eks_inform import getEksCluster, getEksDescription
from board.models import Token
from accounts.models import Groups
from django.contrib.auth.decorators import login_required

import os
import sys
import subprocess
import boto3


# 로그인 후 메인 페이지
def mainPage(request):
    if request.user.is_authenticated:
        access_key_set = Token.objects.filter(group=request.user.group).values('aws_access_key_id')
        secret_key_set = Token.objects.filter(group=request.user.group).values('aws_secret_access_key')
        context = getEksDescription(access_key_set, secret_key_set, region)
        return render(request, 'board/main.html', context)
    else:
        return render(request, 'board/main_not.html')


@login_required(login_url='/accounts/login')
def deleteAwsKeyId(request):
    token = Token.objects.get(group=request.user.group)
    token.aws_access_key_id = ''
    token.save()
    return redirect('/')


@login_required(login_url='/accounts/login')
def deleteAwsSecretkey(request):
    token = Token.objects.get(group=request.user.group)
    token.aws_secret_access_key = ''
    token.save()
    return redirect('/')


@login_required(login_url='/accounts/login')
def deleteGitToken(request):
    token = Token.objects.get(group=request.user.group)
    token.github_access_token = ''
    token.save()
    return redirect('/')


@login_required(login_url='/accounts/login')
def getTokenPage(request):
    if request.method == "GET":
        aws_access_key_id = Token.objects.filter(group=request.user.group).values('aws_access_key_id')
        aws_secret_access_key = Token.objects.filter(group=request.user.group).values('aws_secret_access_key')
        github_access_token = Token.objects.filter(group=request.user.group).values('github_access_token')
        print('aws',aws_access_key_id,aws_secret_access_key)

        context = {
            'aak': aws_access_key_id,
            'asa':aws_secret_access_key,
            'gat':github_access_token
        }
        return render(request, 'board/token_output.html',context)

@login_required(login_url='/accounts/login')
def startci(request):
    if request.method == "GET":
        access_key_set = Token.objects.filter(group=request.user.group).values('aws_access_key_id')
        secret_key_set = Token.objects.filter(group=request.user.group).values('aws_secret_access_key')
        context = getRepoDescription(access_key_set, secret_key_set, region)
        print(context)
        return render(request, 'board/startci.html',context)

    # githubrepo_address, job_name, repository name

@login_required(login_url='/accounts/login')
def startcicd(request):
    if request.method == "GET":
        access_key_set = Token.objects.filter(group=request.user.group).values('aws_access_key_id')
        secret_key_set = Token.objects.filter(group=request.user.group).values('aws_secret_access_key')

        eks_list = getEksCluster(access_key_set, secret_key_set, region)
        repo_list = getRepoName(access_key_set, secret_key_set, region)
        context = {'eks_list':eks_list, 'repo_list':repo_list}
        print(context)
        return render(request, 'board/startcicd.html',context)
    if request.method == "POST":

        githubrepo_address = request.POST.get('githubrepo_address', None)
        repo_name = request.POST.get('repository_name', None)
        cluster_name = request.POST.get('cluster_name', None)
        region = request.POST.get('region',None)

        if (not githubrepo_address):
            print(githubrepo_address)

            # user 아이디 가져오기
            userid = request.user.username

            # key 가져오기
            aws_access_key_id = Token.objects.filter(group=request.user.group).values('aws_access_key_id')
            aws_secret_access_key = Token.objects.filter(group=request.user.group).values('aws_secret_access_key')
            github_access_token = Token.objects.filter(group=request.user.group).values('github_access_token')

            # shell 을 통해 jenkins 에 데이터 전달 및 실행
            subprocess.Popen(['setjenkins.sh %s %s %s %s %s %s %s %s' % (
            userid, repo_name, cluster_name,githubrepo_address, aws_access_key_id, aws_secret_access_key, github_access_token, region)], shell=True)
            context = {
                'githubrepo_address': githubrepo_address
            }
            return render(request, 'board/githubrepo_output.html', context)

        else:
            return redirect('/')

region = 'ap-northeast-2'

@login_required(login_url='/accounts/login')
def eks_list(request):
    ''' 클러스터 목록 조회'''
    access_key_set = Token.objects.filter(group=request.user.group).values('aws_access_key_id')
    secret_key_set = Token.objects.filter(group=request.user.group).values('aws_secret_access_key')
    context = getEksCluster(access_key_set, secret_key_set, region)
    return render(request, 'board/inform_cluster_list.html', context)

@login_required(login_url='/accounts/login')
def eks_des(request):
    ''' 모든 클러스터에 대한 상세정보 조회'''
    access_key_set = Token.objects.filter(group=request.user.group).values('aws_access_key_id')
    secret_key_set = Token.objects.filter(group=request.user.group).values('aws_secret_access_key')
    context = getEksDescription(access_key_set, secret_key_set, region)
    return render(request, 'board/inform_cluster_detail.html', context)

@login_required(login_url='/accounts/login')
def repo_des(request):
    ''' 모든 레포지토리에 대한 상세정보 조회'''
    access_key_set = Token.objects.filter(group=request.user.group).values('aws_access_key_id')
    secret_key_set = Token.objects.filter(group=request.user.group).values('aws_secret_access_key')
    context = getRepoDescription(access_key_set, secret_key_set, region)
    return render(request, 'board/inform_repo_detail.html', context)