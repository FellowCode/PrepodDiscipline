from django.db.models import Count
from django.shortcuts import render
from Disciplines.models import Discipline


def index(request):
    if request.user.is_superuser:
        dis_errors = len(Discipline.objects.filter(errors=True).all()) > 0
        dis_errors = dis_errors or Discipline.objects.annotate(num_nagruzki=Count('nagruzki')).filter(
            num_nagruzki__lte=0).count() > 0
    elif request.user.is_authenticated and request.user.prepod.count() > 0:
        dis_errors = len(Discipline.objects.filter(errors=True, kafedra=request.user.prepod.first().kafedra).all()) > 0
        dis_errors = dis_errors or Discipline.objects.filter(kafedra=request.user.prepod.first().kafedra).annotate(num_nagruzki=Count('nagruzki')).filter(
            num_nagruzki__lte=0).count() > 0
    else:
        dis_errors = True

    return render(request, 'Main/Index.html', {'dis_errors': dis_errors})
