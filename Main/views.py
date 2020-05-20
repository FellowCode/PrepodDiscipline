from django.shortcuts import render
from Disciplines.models import Discipline




def index(request):

    dis_errors = len(Discipline.objects.filter(errors=True).all()) > 0

    return render(request, 'Main/Index.html', {'dis_errors': dis_errors})
