from django.db import models
from django.contrib.auth.models import AbstractUser

class Groups(models.Model):
    name = models.TextField(unique = True)
    # 그룹 요금
    money = models.IntegerField()
    # 그룹에 가입하기 위한 비밀번호
    grouppassword = models.TextField()
    def __str__(self):
        return self.name

class User(AbstractUser):
    group = models.ForeignKey(Groups,on_delete=models.CASCADE)
    isleader = models.BooleanField(default=False)
    # 그룹에 가입하기 위해 입력한 그룹 비밀번호 저장 - 비밀번호 비교를 위해
    gpass = models.TextField()
    pass