from accounts.models import User
from django.shortcuts import render, redirect
from django.db.models import Q
from django.db import connection
# Create your views here.
def mainPage(request):
    return render(request, 'board/main.html')

def awsInputPage(request):
    if request.method == "GET":
        return render(request, 'board/aws_input.html')
    if request.method == "POST":
        aws_access_key_id = request.POST.get('aws_access_key_id',None)
        aws_secret_access_key = request.POST.get('aws_secret_access_key', None)

        user = User.objects.get(id=request.user.id)
        user.aws_access_key_id = aws_access_key_id
        user.aws_secret_access_key = aws_secret_access_key
        user.save()

        #cursor = connection.cursor()
        #strsql = "SELECT id,username,aws_access_token FROM accounts_user"
        #result = cursor.execute(strsql)
        #st = cursor.fetchall()
        #connection.commit()
        #connection.close()
        #print('st', st)


        context = {
            'aws_access_key_id' : aws_access_key_id,
            'aws_secret_access_key' : aws_secret_access_key
        }
        return render(request,'board/aws_output.html',context)


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