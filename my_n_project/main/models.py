from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from django.contrib.auth.models import PermissionsMixin
from django.db.models import DateTimeField
from django.utils import timezone


class MyUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    city = models.CharField(max_length=100, blank=True)
    nick = models.CharField(max_length=30, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = MyUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

class Challenges(models.Model):

    owner = models.CharField(max_length=30)
    added_friend = models.CharField(max_length=30)
    title = models.CharField(max_length=30)
    descr = models.CharField(max_length=30)
    duration = models.IntegerField()
    progress = models.IntegerField()
    is_active = models.BooleanField()
    score_for_win = models.IntegerField()
    deadline = models.DateField(default=timezone.now)

class FriendShip(models.Model):
    user = models.CharField(max_length=30)
    friend = models.CharField(max_length=30)
    confirmed = models.BooleanField()

class Comment(models.Model):
    challenge = models.ForeignKey(Challenges, on_delete=models.CASCADE, default=None)
    text = models.CharField(max_length=10)


