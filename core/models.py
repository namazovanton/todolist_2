from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    REQUIRED_FIELDS = []
    username = models.CharField(max_length=30, unique=True)
    email = models.EmailField(max_length=40, unique=True, null=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    last_login = models.DateField()
    date_joined = models.DateField()
