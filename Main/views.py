from django.shortcuts import render
from Disciplines.models import Discipline




def index(request):
    if request.user.is_superuser:
        dis_errors = len(Discipline.objects.filter(errors=True).all()) > 0
    elif hasattr(request.user, 'prepod'):
        dis_errors = len(Discipline.objects.filter(errors=True, kafedra=request.user.prepod.kafedra).all()) > 0
    else:
        dis_errors = True

    return render(request, 'Main/Index.html', {'dis_errors': dis_errors})
