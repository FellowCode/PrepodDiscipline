from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.http import JsonResponse, Http404
from django.shortcuts import render

from Prepods.models import Prepod
from Disciplines.models import Discipline, Kafedra
from utils.decorators import prepod_only
from utils.shortcuts import iredirect

from utils.xls import create_prep_ds_xls
from Accounts.models import User
from .forms import *


@login_required
@prepod_only
def prepods_list(request):
    if request.user.is_superuser:
        prepods = Prepod.objects.all()
    elif request.user.prepod.count() == 0:
        return iredirect('main:index')
    else:
        prepods = Prepod.objects.filter(kafedra=request.user.prepod.first().kafedra)
    return render(request, 'Prepods/List.html', {'prepods': prepods})

@login_required
@prepod_only
def prepod_disciplines(request, id):
    prepod = Prepod.objects.get_or_404(id=id)
    if request.user.is_superuser and request.is_ajax() and request.method == 'POST':
        discpl_id = request.POST.getlist('discipline', [])
        ds = Discipline.objects.filter(id__in=discpl_id)
        for d in ds:
            d.prepod = prepod
        Discipline.objects.bulk_update(ds, ['prepod'])
        ds = Discipline.objects.all().difference(ds)
        for d in ds:
            d.prepod = None
        Discipline.objects.bulk_update(ds, ['prepod'])
        return JsonResponse({'status': 'OK'})
    if request.user.is_superuser:
        disciplines = Discipline.objects.all()
    else:
        disciplines = prepod.disciplines.all()
    return render(request, 'Prepods/Disciplines.html', {'prepod': prepod, 'disciplines': disciplines})

@login_required
@prepod_only
def prep_ds_download(request, id):
    prepod = Prepod.objects.get_or_404(id=id)
    if request.is_ajax() and request.method == 'POST' and (request.user.is_superuser or request.user.prepod == prepod):
        url, filename = create_prep_ds_xls(prepod)
        return JsonResponse({'status': 'OK', 'url': url, 'filename': filename})
    raise Http404


@login_required
@prepod_only
def prepod_form(request, id=None):
    prepod = Prepod.objects.get_or_none(id=id)
    form = PrepodForm(instance=prepod)
    if request.method == 'POST':
        form = PrepodForm(request.POST, instance=prepod)
        if form.is_valid():
            prepod = form.save(commit=False)
            if not request.user.is_superuser:
                prepod.kafedra = request.user.prepod.first().kafedra
            prepod.save()
            return iredirect('prepods:list')
    return render(request, 'Prepods/Form.html', {'form': form, 'kafedri': Kafedra.objects.all(), 'users': User.objects.all()})
