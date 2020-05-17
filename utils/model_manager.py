from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.contrib.auth.base_user import BaseUserManager
from django.http import Http404


class MyManager(models.Manager):

    def get_or_none(self, **kwargs):
        try:
            return self.get(**kwargs)
        except ObjectDoesNotExist:
            return None

    def get_or_404(self, **kwargs):
        obj = self.get_or_none(**kwargs)
        if obj:
            return obj
        raise Http404

    def get_list_or_none(self, **kwargs):
        obj_list = self.filter(**kwargs).all()
        if len(obj_list) == 0:
            return None
        return obj_list

    def get_or_new(self, **kwargs):
        try:
            return self.get(**kwargs)
        except ObjectDoesNotExist:
            return self.model(**kwargs)


    def resave_all(self):
        objs = self.all()
        for obj in objs:
            obj.save()


class MyUserManager(BaseUserManager, MyManager):
    """
        Custom user model manager where email is the unique identifiers
        for authentication instead of usernames.
        """

    def create_user(self, email, password, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not email:
            raise ValueError(_('The Email must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(email, password, **extra_fields)
