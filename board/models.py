from django.db import models
from accounts.models import User
from accounts.models import Groups

class Token(models.Model):
    group = models.ForeignKey(Groups,on_delete=models.CASCADE)
    aws_access_key_id = models.TextField()
    aws_secret_access_key = models.TextField()
    github_access_token = models.TextField()
    jenkins_access_token = models.TextField()

class Build(models.Model):
    group = models.ForeignKey(Groups,on_delete=models.CASCADE)
    username = models.TextField()
    result = models.TextField()
    time = models.TextField()
    cicd = models.TextField()
    repo = models.TextField()
    cluster = models.TextField()
    git = models.TextField()