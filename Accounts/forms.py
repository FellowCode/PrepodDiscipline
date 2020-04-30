from django import forms
from django.contrib.auth import authenticate

from Accounts.models import User


class LoginForm(forms.Form):
    email = forms.CharField(required=True)

    password = forms.CharField(required=True)

    def clean(self):
        email = self.cleaned_data.get('email', '')
        password = self.cleaned_data.get('password', '')
        user = authenticate(username=email, password=password)
        if not user:
            self.add_error("email", "Неправильный логин или пароль")
            self.add_error("password", "Неправильный логин или пароль")
        self.cleaned_data['user'] = user
        return self.cleaned_data


class RegistrationForm(forms.Form):
    email = forms.CharField(required=True)

    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)

    fpassword = forms.CharField(required=True)
    spassword = forms.CharField(required=True)

    def clean_email(self):
        email = self.cleaned_data['email']
        user = User.objects.get_or_none(email=email)
        if user:
            self.add_error("email", "Такой email уже используется")
        return email

    def clean_fpassword(self):
        password = self.cleaned_data['fpassword']
        if len(password) < 8:
            self.add_error("fpassword", "Не менее 8 сиволов")
        if ';' in password:
            self.add_error("fpassword", "Недопустимый символ в пароле")
        return password

    def clean_spassword(self):
        firstpassword = self.cleaned_data['fpassword']
        secondpassword = self.cleaned_data['spassword']
        if firstpassword != secondpassword:
            self.add_error("spassword", "Пароли не совпадают")
        return secondpassword


class ChangePasswordForm(forms.Form):
    old_password = forms.CharField()

    fpassword = forms.CharField()
    spassword = forms.CharField()

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)

    def clean_old_password(self):
        password = self.cleaned_data['old_password']
        user = authenticate(username=self.user.email, password=password)
        if not user:
            self.add_error('old_password', 'Неверный пароль')
        return password

    def clean_fpassword(self):
        password = self.cleaned_data['fpassword']
        if len(password) < 8:
            self.add_error("fpassword", "Не менее 8 символов")
        if ';' in password:
            self.add_error("fpassword", "Недопустимый символ в пароле")
        return password

    def clean_spasswods(self):
        firstpassword = self.cleaned_data['fpassword']
        secondpassword = self.cleaned_data['spassword']
        if firstpassword != secondpassword:
            self.add_error("spassword", "Пароли не совпадают")
        return secondpassword