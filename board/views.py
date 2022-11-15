from accounts.models import User
from django.shortcuts import render
from django.db.models import Q

# Create your views here.
def mainPage(request):
    return render(request, 'board/main.html')

def awsInputPage(request):
    if request.method == "GET":
        return render(request, 'board/aws_input.html')
    if request.method == "POST":
        aws_access_token = request.POST.get('aws_access_token',None)
        user = User.objects.get(id=request.user.id)
        user.aws_access_token = aws_access_token
        user.save()

        context = {
            'aws_access_token' : aws_access_token
        }
        return render(request,'board/aws_output.html',context)

def githubInputPage(request):
    if request.method == "GET":
        return render(request, 'board/github_input.html')
    if request.method == "POST":
        github_access_token = request.POST.get('github_access_token', None)
        user = User.objects.get(id=request.user.id)
        user.github_access_token = github_access_token
        user.save()

        context = {
            'github_access_token': github_access_token
        }
        return render(request, 'board/github_output.html',context)

def getTokenPage(request):
    if request.method == "GET":
        aws_access_token = User.objects.filter(id=request.user.id).values('aws_access_token')
        github_access_token = User.objects.filter(id=request.user.id).values('github_access_token')
        print('aws',aws_access_token)
        context = {
            'aat': aws_access_token,
            'gat':github_access_token
        }
        return render(request, 'board/token_output.html',context)