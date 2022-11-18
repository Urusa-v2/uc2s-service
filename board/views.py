from django.shortcuts import render, redirect
from django.db.models import Q
from django.db import connection
from board.models import Token

import os
import sys
import subprocess
import boto3


# Create your views here.
def mainPage(request):
    return render(request, 'board/main.html')


def awsInputPage(request):
    if request.method == "GET":
        return render(request, 'board/aws_input.html')
    if request.method == "POST":
        token = Token.objects.get(user=request.user)
        token.user = request.user
        token.aws_access_key_id = request.POST.get('aws_access_key_id', None)
        token.aws_secret_access_key = request.POST.get('aws_secret_access_key', None)
        if (token.aws_access_key_id != "") and (token.aws_secret_access_key != ""):
            token.save()
            context = {
                'aws_access_key_id': token.aws_access_key_id,
                'aws_secret_access_key': token.aws_secret_access_key
            }
            return render(request, 'board/aws_output.html', context)
        else:
            return redirect('/')


def deleteAwsKeyId(request):
    token = Token.objects.get(user=request.user)
    token.aws_access_key_id = ''
    token.save()
    return redirect('/')


def deleteAwsSecretkey(request):
    token = Token.objects.get(user=request.user)
    token.aws_secret_access_key = ''
    token.save()
    return redirect('/')


def githubInputPage(request):
    if request.method == "GET":
        return render(request, 'board/github_input.html')
    if request.method == "POST":
        token = Token.objects.get(user=request.user)
        token.github_access_token = request.POST.get('github_access_token', None)
        if (token.github_access_token != ""):
            token.user = request.user
            token.save()

            context = {
                'github_access_token': token.github_access_token
            }
            return render(request, 'board/github_output.html', context)
        else:
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
        print('aws', aws_access_key_id, aws_secret_access_key)

        context = {
            'aak': aws_access_key_id,
            'asa': aws_secret_access_key,
            'gat': github_access_token
        }
        return render(request, 'board/token_output.html', context)


def startcicd(request):
    if request.method == "GET":
        return render(request, 'board/startcicd.html')
    if request.method == "POST":
        githubrepo_address = request.POST.get('githubrepo_address', None)
        if (not githubrepo_address):
            print(githubrepo_address)

            # key 가져오기
            aws_access_key_id = Token.objects.filter(user_id=request.user.id).values('aws_access_key_id')
            aws_secret_access_key = Token.objects.filter(user_id=request.user.id).values('aws_secret_access_key')
            github_access_token = Token.objects.filter(user_id=request.user.id).values('github_access_token')

            # shell 을 통해 jenkins 에 데이터 전달 및 실행
            subprocess.Popen(['setjenkins.sh %s %s %s %s' % (
            githubrepo_address, aws_access_key_id, aws_secret_access_key, github_access_token)], shell=True)
            context = {
                'githubrepo_address': githubrepo_address
            }
            return render(request, 'board/githubrepo_output.html', context)

        else:
            return redirect('/')


def eks_list(request):
    ''' 클러스터 목록 조회'''
    access_key_set = Token.objects.filter(user=request.user).values('aws_access_key_id')
    secret_key_set = Token.objects.filter(user=request.user).values('aws_secret_access_key')
    for access_key_s, secret_key_s in zip(access_key_set, secret_key_set):
        access_key = access_key_s['aws_access_key_id']
        secret_key = secret_key_s['aws_secret_access_key']
        region = 'ap-northeast-2'

        client = boto3.client(
            'eks',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )

        response = client.list_clusters()
        context = {'clusters': response['clusters']}
        print(response['clusters'])
        return render(request, 'board/inform_cluster_list.html', context)
        # response = ''


def eks_des(request):
    ''' 모든 클러스터에 대한 상세정보 조회'''
    access_key_set = Token.objects.filter(user=request.user).values('aws_access_key_id')
    secret_key_set = Token.objects.filter(user=request.user).values('aws_secret_access_key')
    for access_key_s, secret_key_s in zip(access_key_set, secret_key_set):
        access_key = access_key_s['aws_access_key_id']
        secret_key = secret_key_s['aws_secret_access_key']
        region = 'ap-northeast-2'

        client = boto3.client(
            'eks',  # 서비스 이름
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )

        response = client.list_clusters()

        c_list = response
        response = ''

        for i in c_list['clusters']:
            response = client.describe_cluster(
                name=i
            )

        context = {'cluster_name': response['cluster']['name'],
                   'end_point': response['cluster']['endpoint'],
                   'ip': response['cluster']['kubernetesNetworkConfig']['serviceIpv4Cidr']}
        print('#cluster name :', response['cluster']['name'], '#end point :', response['cluster']['endpoint'], '#IP :',
              response['cluster']['kubernetesNetworkConfig']['serviceIpv4Cidr'])
        return render(request, 'board/inform_cluster_detail.html', context)


def repo_des(request):
    ''' 모든 레포지토리에 대한 상세정보 조회'''
    access_key_set = Token.objects.filter(user=request.user).values('aws_access_key_id')
    secret_key_set = Token.objects.filter(user=request.user).values('aws_secret_access_key')
    for access_key_s, secret_key_s in zip(access_key_set, secret_key_set):
        access_key = access_key_s['aws_access_key_id']
        secret_key = secret_key_s['aws_secret_access_key']

        region = 'ap-northeast-2'
        client = boto3.client(
            'ecr',  # 서비스 이름
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )
        response = client.describe_repositories()
        context = {'repo_name': response['repositories'][0]['repositoryName'],
                   'repo_uri': response['repositories'][0]['repositoryUri']}
        print('#repo name :', response['repositories'][0]['repositoryName'], '#repo uri :',
              response['repositories'][0]['repositoryUri'])
        return render(request, 'board/inform_repo_detail.html', context)