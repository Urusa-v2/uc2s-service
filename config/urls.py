"""config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

import accounts.views
import board.views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',board.views.mainPage),
    path('board/awsInputPage',board.views.awsInputPage),
    path('board/githubInputPage',board.views.githubInputPage),
    path('board/getTokenPage',board.views.getTokenPage),

    path('board/aws_key_id_delete',board.views.deleteAwsKeyId),
    path('board/aws_secret_key_delete',board.views.deleteAwsSecretkey),
    path('board/github_token_delete',board.views.deleteGitToken),
    path('accounts/signup', accounts.views.singup),
    path('accounts/signout', accounts.views.signout),
    path('accounts/login', accounts.views.login),
    path('accounts/logout', accounts.views.logout),
    path('board/startcicd',board.views.startcicd),

]
