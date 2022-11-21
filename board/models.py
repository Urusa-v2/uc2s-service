from django.db import models
from accounts.models import User

class Token(models.Model):
    group = models.TextField(unique = True)
    aws_access_key_id = models.TextField()
    aws_secret_access_key = models.TextField()
    github_access_token = models.TextField()
    jenkins_access_token = models.TextField()