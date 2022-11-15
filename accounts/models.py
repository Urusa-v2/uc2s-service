from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.
class User(AbstractUser):
    # 기본적으로 제공하는 필드 외에 원하는 필드
    aws_access_token = models.TextField()
    github_access_token = models.TextField()