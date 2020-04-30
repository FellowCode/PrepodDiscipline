from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from utils.model_manager import MyUserManager


class User(AbstractBaseUser, PermissionsMixin):
    objects = MyUserManager()
    # Поля таблицы User
    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)
    surname = models.CharField(max_length=64)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)
    mail_dt = models.DateTimeField(default=timezone.now)
    is_confirm = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def get_salt(self):
        return self.email

    class Meta:
        ordering = ['id']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.email
