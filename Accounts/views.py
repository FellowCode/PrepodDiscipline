import urllib

from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render, redirect
from django.urls import reverse

from .forms import *
from django.contrib import auth
from django.conf import settings
from django.db.models import Q
import re
from urllib.parse import unquote
import json


def login(request):
    if not request.user.is_authenticated:
        if request.method == 'POST':
            form = LoginForm(request.POST)
            if form.is_valid():
                auth.login(request, form.cleaned_data['user'])
                if request.GET.get('next'):
                    return redirect(request.GET['next'])
                return redirect(reverse('main:index'))
            for error in form['email'].errors:
                print(error)
            return render(request, 'Accounts/Login.html', {'form': form})
        form = LoginForm()
        return render(request, 'Accounts/Login.html', {'form': form})
    return redirect(reverse('main:index'))


def admin_login(request):
    p = urllib.parse.urlencode(request.GET)
    return redirect(f'{settings.LOGIN_URL}?' + p)


@login_required
def logout(request):
    auth.logout(request)
    return redirect(reverse('main:index'))


def registration(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(email=form.cleaned_data['email'],
                                            password=form.cleaned_data['fpassword'])
            auth.login(request, user)
            return redirect(reverse('main:index'))
        return render(request, 'Accounts/Registration.html', {'form': form})
    form = RegistrationForm()
    return render(request, 'Accounts/Registration.html', {'form': form})


@login_required
def change_password(request):
    if not request.method == 'POST':
        form = ChangePasswordForm(user=request.user)
        return render(request, 'Accounts/ChangePassword.html', {'form': form})
    # POST
    form = ChangePasswordForm(request.POST, user=request.user)
    if form.is_valid():
        request.user.set_password(form.cleaned_data['spassword'])
        request.user.save()
        auth.login(request, request.user)
        return redirect(reverse('accounts:personal_area'))
    return render(request, 'Accounts/ChangePassword.html', {'form': form})