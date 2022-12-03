from datetime import datetime
from django.shortcuts import render, redirect
from django.db.models import Q
from django.db import connection

from api.ecr_inform import getRepoDescription, getRepoName
from api.eks_inform import getEksCluster, getEksDescription
from api.cost_inform import getCost, ec2Cost
from board.models import Token
from board.models import Build
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

        # group 의 서비스 이용 요금
        group = request.user.group
        money = group.money
        context = { 'eks' : getEksDescription(access_key_set, secret_key_set, region), 'cost' : getCost(access_key_set,secret_key_set,region), 'ec2cost' : ec2Cost(access_key_set,secret_key_set,region), 'money':money }
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
        # 선택한 region 을 url 에 담아서 보내준다
        region = request.POST.get('region')
        return redirect('/board/startci/'+str(region))

def selectRegionCICD(request):
    if request.method == "GET":
        return render(request, 'board/selectRegion_cicd.html')
    elif request.method == "POST":
        # 선택한 region 을 url 에 담아서 보내준다
        region = request.POST.get('region')
        return redirect('/board/startcicd/'+str(region))

@login_required(login_url='/accounts/login')
def startci(request,rname): # rname 은 리전 선택창에서 선택한 리전을 url 에 담아서 보내주므로, 이를 받아오는 변수이다
    if request.method == "GET":
        #selectRegion 에서 선택한 region 데이터를 region 변수에 설정한다
        region = rname
        # 리전의 ecr 리스트를 조회하기 위하여 AWS KEY 를 가져온다
        access_key_set = Token.objects.filter(group=request.user.group).values('aws_access_key_id')
        secret_key_set = Token.objects.filter(group=request.user.group).values('aws_secret_access_key')
        # ecr repo list 를 조회하여 보내서 사용자가 repo 를 선택하게 한다
        repo_list = getRepoDescription(access_key_set, secret_key_set, region)
        context = {'repo_list':repo_list,'region':region}
        print(context)
        return render(request, 'board/startci.html',context)

    elif request.method == "POST":
        githubrepo_address = request.POST.get('githubrepo_address', None)

        if githubrepo_address is not None: # github repo 주소를 잘 작성했을 경우
          region = request.POST.get('region', None)
          repo_name = request.POST.get('repository_name', None)
        
          # 키 가져오기
          # key 가져오기. filter 로 가져오면 list 형태로 반환되므로,
          # Model 객체를 가져와서 해당 객체의 속성 값을 통해 AWS Key 값을 가져온다
          token = Token.objects.get(group=request.user.group)
          aws_access_key_id = token.aws_access_key_id
          aws_secret_access_key = token.aws_secret_access_key

          # cicd 설정 변수
          way = 'ci'

          # group 아이디 가져오기
          group = request.user.group
          userid = group.name
          
          # ci 만 수행할 시 cluster name 은 필요 없으므로 None ( Null ) 로 설정한다. 이는 코드와 파일의 재활용성을 높이기 위해 동일한 shell 파일을 사용하기 위함이다
          # 표준 입출력에 대해 Pipe 를 열어서 build 성공 여부를 가져온다
          result = subprocess.Popen(['/var/www/django/board/calljenkins.sh %s %s %s %s %s %s %s %s' % (userid, repo_name, None, githubrepo_address, aws_access_key_id, aws_secret_access_key, region, way)],shell=True, stdout=subprocess.PIPE)

          # 현재 작업 실행 시간 가져오기
          now = datetime.now()
          nowtime = now.strftime('%Y-%m-%d %H:%M:%S')

          # 작업 이력을 저장할 Bulid 객체 생성 및 데이터 지정
          build = Build()
          build.group = request.user.group
          build.username = request.user.username
          build.cicd = way
          build.time = nowtime
          build.repo = repo_name
          build.git = githubrepo_address
          build.cluster = "No Cluster"

          # group 이용 금액 증가
          group.money += 1000
          group.save()

          if result == "Finished: SUCCESS":  # build 성공창 출력
              # build 기록에 성공 여부 지정
              build.result = "Success"
              # 작업 이력 저장
              build.save()
              return render(request, 'board/successpage.html')
          else:  # build 실패창 출력
              # build 기록에 성공 여부 지정
              build.result = "Fail"
              # 작업 이력 저장
              build.save()
              return render(request, 'board/successpage.html')
        else:
          return redirect('/')  

@login_required(login_url='/accounts/login')
def startcicd(request,rname): # rname 은 리전 선택창에서 선택한 리전을 url 에 담아서 보내주므로, 이를 받아오는 변수이다
    if request.method == "GET":
        # selectRegion 에서 선택한 region 데이터를 region 변수에 설정한다
        region = rname
        access_key_set = Token.objects.filter(group=request.user.group).values('aws_access_key_id')
        secret_key_set = Token.objects.filter(group=request.user.group).values('aws_secret_access_key')
        # eks cluster list 와 repo list 를 담아서 보내주어 사용자가 이를 보고 선택할 수 있게 한다
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

            # group 아이디 가져오기
            group = request.user.group
            userid = group.name

            # key 가져오기. filter 로 가져오면 list 형태로 반환되므로,
            # Model 객체를 가져와서 해당 객체의 속성 값을 통해 AWS Key 값을 가져온다
            token = Token.objects.get(group=request.user.group)
            aws_access_key_id = token.aws_access_key_id
            aws_secret_access_key = token.aws_secret_access_key

            # ci cd 설정 변수
            way = 'cicd'
            # shell 을 통해 jenkins 에 데이터 전달 및 실행
            # 표준 입출력에 대해 Pipe 를 열어서 build 성공 여부를 가져온다
            result = subprocess.Popen(['/var/www/django/board/calljenkins.sh %s %s %s %s %s %s %s %s' % (userid, repo_name, cluster_name, githubrepo_address, aws_access_key_id, aws_secret_access_key, region,way)], shell=True, stdout=subprocess.PIPE)

            # 현재 작업 실행 시간 가져오기
            now = datetime.now()
            nowtime = now.strftime('%Y-%m-%d %H:%M:%S')

            # 작업 이력을 저장할 Bulid 객체 생성 및 데이터 지정
            build = Build()
            build.group = request.user.group
            build.username = request.user.username
            build.cicd = way
            build.git = githubrepo_address
            build.time = nowtime
            build.repo = repo_name
            build.cluster = cluster_name

            # group 이용 금액 증가
            group.money += 1000
            group.save()

            if result == "Finished: SUCCESS": #build 성공창 출력
                # build 기록에 성공 여부 지정
                build.result = "Success"
                # 작업 이력 저장
                build.save()
                return render(request, 'board/successpage.html')
            else: # build 실패창 출력
                # build 기록에 성공 여부 지정
                build.result = "Fail"
                # 작업 이력 저장
                build.save()
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

def terms_and_conditions(request):
    return render(request, 'board/terms_and_conditions.html')

@login_required(login_url='/accounts/login')
def buildhistroy(request):
    build_id = Build.Objects.filter(group=request.user.group).values('id')
    username = Build.Objects.filter(group=request.user.group).values('username')
    result = Build.Objects.filter(group=request.user.group).values('result')
    time = Build.Objects.filter(group=request.user.group).values('time')
    cicd = Build.Objects.filter(group=request.user.group).values('cicd')
    repo = Build.Objects.filter(group=request.user.group).values('repo')
    cluster = Build.Objects.filter(group=request.user.group).values('cluster')
    git = Build.Objects.filter(group=request.user.group).values('git')
    dict_list = zip(build_id,username,result,time,cicd,repo,cluster,git)
    print(dict_list)
    context = {'dict_list':dict_list, 'build_id':build_id, 'username':username, 'result':result, 'time':time, 'cicd':cicd, 'repo':repo, 'cluster':cluster, 'git':git}
    return render(request, 'board/showbuildhistory.html', context)
