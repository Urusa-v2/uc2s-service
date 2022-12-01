from django.shortcuts import render, redirect
from django.db.models import Q
from django.db import connection

from api.ecr_inform import getRepoDescription, getRepoName
from api.eks_inform import getEksCluster, getEksDescription
from api.cost_inform import getCost
from board.models import Token
from accounts.models import Groups
from django.contrib.auth.decorators import login_required

import os
import sys
import subprocess
import boto3

region = 'ap-northeast-2'

# 로그인 후 메인 페이지
def mainPage(request):
    if request.user.is_authenticated:
        access_key_set = Token.objects.filter(group=request.user.group).values('aws_access_key_id')
        secret_key_set = Token.objects.filter(group=request.user.group).values('aws_secret_access_key')
        context = { 'eks' : getEksDescription(access_key_set, secret_key_set, region), 'cost' : getCost(access_key_set,secret_key_set,region) }
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

def selectRegionCI(request):
    if request.method == "GET":
        return render(request, 'board/selectRegion_ci.html')
    elif request.method == "POST":
        region = request.POST.get('region')
        return redirect('/board/startci/'+str(region))

def selectRegionCICD(request):
    if request.method == "GET":
        return render(request, 'board/selectRegion_cicd.html')
    elif request.method == "POST":
        region = request.POST.get('region')
        return redirect('/board/startcicd/'+str(region))

@login_required(login_url='/accounts/login')
def startci(request,rname):
    if request.method == "GET":
        region = rname
        access_key_set = Token.objects.filter(group=request.user.group).values('aws_access_key_id')
        secret_key_set = Token.objects.filter(group=request.user.group).values('aws_secret_access_key')
        repo_list = getRepoDescription(access_key_set, secret_key_set, region)
        context = {'repo_list':repo_list,'region':region}
        print(context)
        return render(request, 'board/startci.html',context)


    elif request.method == "POST":

        githubrepo_address = request.POST.get('githubrepo_address', None)

        if githubrepo_address is not None:
          region = request.POST.get('region', None)
          repo_name = request.POST.get('repository_name', None)
        
          # 키 가져오기
          token = Token.objects.get(group=request.user.group)
          aws_access_key_id = token.aws_access_key_id
          aws_secret_access_key = token.aws_secret_access_key

          # cicd 설정 변수
          way = 'ci'
          # user 아이디 가져오기
          userid = request.user.username
          # ci 만 수행할 시 cluster name 은 필요 없으므로 None ( Null ) 로 설정한다. 이는 코드와 파일의 재활용성을 높이기 위해 동일한 shell 파일을 사용하기 위함이다
          subprocess.Popen(['/var/www/django/board/calljenkins.sh %s %s %s %s %s %s %s %s' % (userid, repo_name, None, githubrepo_address, aws_access_key_id, aws_secret_access_key, region, way)],shell=True)
          return render(request, 'board/successpage.html')
        else:
          return redirect('/')  

@login_required(login_url='/accounts/login')
def startcicd(request,rname):
    if request.method == "GET":
        region = rname
        access_key_set = Token.objects.filter(group=request.user.group).values('aws_access_key_id')
        secret_key_set = Token.objects.filter(group=request.user.group).values('aws_secret_access_key')

        eks_list = getEksCluster(access_key_set, secret_key_set, region)
        repo_list = getRepoDescription(access_key_set, secret_key_set, region)
        context = {'eks_list':eks_list, 'repo_list':repo_list, 'region':region}
        return render(request, 'board/startcicd.html',context)
    if request.method == "POST":
        region = request.POST.get('region', None)
        githubrepo_address = request.POST.get('githubrepo_address', None)
        repo_name = request.POST.get('repository_name', None)
        cluster_name = request.POST.get('cluster_name', None)
        if githubrepo_address is not None:

            # user 아이디 가져오기
            userid = request.user.username

            # key 가져오기
            token = Token.objects.get(group=request.user.group)
            aws_access_key_id = token.aws_access_key_id
            aws_secret_access_key = token.aws_secret_access_key

            # ci cd 설정 변수
            way = 'cicd'
            # shell 을 통해 jenkins 에 데이터 전달 및 실행
            subprocess.Popen(['/var/www/django/board/calljenkins.sh %s %s %s %s %s %s %s %s' % (userid, repo_name, cluster_name, githubrepo_address, aws_access_key_id, aws_secret_access_key, region,way)], shell=True)
            return render(request, 'board/successpage.html')

        else:
            return redirect('/')



@login_required(login_url='/accounts/login')
def eks_list(request):
    ''' 클러스터 목록 조회'''
    access_key_set = Token.objects.filter(group=request.user.group).values('aws_access_key_id')
    secret_key_set = Token.objects.filter(group=request.user.group).values('aws_secret_access_key')
    context = getEksCluster(access_key_set, secret_key_set, region)
    return render(request, 'board/inform_cluster_list.html', context)

@login_required(login_url='/accounts/login')
def eks_des(request):
    region = request.GET.get('region')
    print('region',region)
    if region != None:
        ''' 모든 클러스터에 대한 상세정보 조회'''
        access_key_set = Token.objects.filter(group=request.user.group).values('aws_access_key_id')
        secret_key_set = Token.objects.filter(group=request.user.group).values('aws_secret_access_key')
        context = getEksDescription(access_key_set, secret_key_set, region)
    else:
        context = {}
    return render(request, 'board/inform_cluster_detail.html', context)

@login_required(login_url='/accounts/login')
def repo_des(request):
    region = request.GET.get('region')
    print(region)
    ''' 모든 레포지토리에 대한 상세정보 조회'''
    if region != None:
        access_key_set = Token.objects.filter(group=request.user.group).values('aws_access_key_id')
        secret_key_set = Token.objects.filter(group=request.user.group).values('aws_secret_access_key')
        context = getRepoDescription(access_key_set, secret_key_set, region)
    else:
        context = {}
    return render(request, 'board/inform_repo_detail.html', context)

def contact(request):
    return render(request, 'board/contact.html')