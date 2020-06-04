from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.http import FileResponse, Http404
from django.shortcuts import render
from Disciplines.models import Discipline
from utils.decorators import prepod_only
from utils.shortcuts import check_discipline_errors, iredirect
from utils.word import word_shtat_rasp
from utils.xls import excel_shtat_rasp


def index(request):
    return render(request, 'Main/Index.html', {'dis_errors': check_discipline_errors(request)})
