from django.db import models
from accounts.models import User
from accounts.models import Groups

class Token(models.Model):
    group = models.ForeignKey(Groups,on_delete=models.CASCADE)
    aws_access_key_id = models.TextField()
    aws_secret_access_key = models.TextField()
    github_access_token = models.TextField()
    jenkins_access_token = models.TextField()