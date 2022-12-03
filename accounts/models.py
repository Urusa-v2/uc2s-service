from django.db import models
from django.contrib.auth.models import AbstractUser

class Groups(models.Model):
    name = models.TextField(unique = True)
    money = models.IntegerField()
    def __str__(self):
        return self.name

class User(AbstractUser):
    group = models.ForeignKey(Groups,on_delete=models.CASCADE)
    isleader = models.BooleanField(default=False)
    pass