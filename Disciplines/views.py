from django.http import HttpResponse
from django.shortcuts import render, reverse
from .models import Discipline

from utils.xls import handle_upload_disciplines

def desciplines_list(request):
    disciplines = Discipline.objects.all()
    return render(request, 'Disciplines/List.html', {'disciplines': disciplines})

def disciplines_upload(request):
    if request.method == 'POST':
        handle_upload_disciplines(request.FILES['file'])
    return HttpResponse()