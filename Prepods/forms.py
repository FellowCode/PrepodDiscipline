from django.forms import ModelForm
from .models import Prepod


class PrepodForm(ModelForm):


    class Meta:
        model = Prepod
        exclude = ['id', 'user']