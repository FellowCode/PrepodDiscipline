from django.shortcuts import render

from Prepods.models import Prepod
from Disciplines.models import Discipline


def prepods_list(request):
    return render(request, 'Prepods/List.html', {'prepods': Prepod.objects.all()})

def prepod_disciplines(request, id):
    prepod = Prepod.objects.get_or_404(id=id)
    return render(request, 'Prepods/Disciplines.html', {'prepod': prepod})

def prepod_available(request, id):
    prepod = Prepod.objects.get_or_404(id=id)
    return render(request, 'Prepods/Available.html', {'prepod': prepod, 'disciplines': Discipline.objects.all()})