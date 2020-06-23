from django import forms

from Disciplines.models import Nagruzka


class NagruzkaForm(forms.ModelForm):
    class Meta:
        model = Nagruzka
        fields = ['prepod', 'n_stavka', 'pochasovka']