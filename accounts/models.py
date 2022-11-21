from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    group = models.TextField()
    isleader = models.BooleanField(default=False)
    pass

class Groups(models.Model):
    name = models.TextField(unique = True)