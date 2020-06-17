from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.db.models import F, Count
from django.http import JsonResponse, Http404, FileResponse
from django.shortcuts import render

from Prepods.models import Prepod
from Disciplines.models import Discipline, Kafedra
from utils.decorators import prepod_only
from utils.shortcuts import iredirect, check_discipline_errors, get_shtat_rasp

from utils.xls import create_prep_cart_xls, Q
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
    prepods = prepods.annotate(num_nagruzki=Count('nagruzki', filter=Q(nagruzki__archive=None)))

    return render(request, 'Prepods/List.html', {'prepods': prepods, 'dis_errors': check_discipline_errors(request)})

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
def prep_cart_download(request):
    prepod = Prepod.objects.get_or_404(id=request.GET.get('id'))
    path = create_prep_cart_xls(request.user, prepod, _type=request.GET.get('type'), stavka=request.GET.get('stavka'))
    return FileResponse(open(path, 'rb'))


@login_required
@prepod_only
def download_prepod_karts(request):
    import os
    import zipfile
    zip_path = 'tmp/zip/'
    filename = f'{request.user.id}-PrepodKarts.zip'
    if not os.path.exists(zip_path):
        os.makedirs(zip_path)
    zip_path += filename
    zipf = zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED)
    prepods = get_shtat_rasp(request)
    for id, prepod in prepods['rows'].items():
        prepod_obj = Prepod.objects.get_or_none(id=id)
        for ir in range(7, 11, 1):
            if prepod[ir] == '':
                prepod[ir] = 0
        path = create_prep_cart_xls(request.user, prepod_obj, _type='b', stavka=prepod[7])
        if path:
            zipf.write(path, path.split('/')[-1])
        path = create_prep_cart_xls(request.user, prepod_obj, _type='b_p', stavka=prepod[8])
        if path:
            zipf.write(path, path.split('/')[-1])
        path = create_prep_cart_xls(request.user, prepod_obj, _type='vb', stavka=prepod[9])
        if path:
            zipf.write(path, path.split('/')[-1])
        path = create_prep_cart_xls(request.user, prepod_obj, _type='vb_p', stavka=prepod[10])
        if path:
            zipf.write(path, path.split('/')[-1])
    zipf.close()
    return FileResponse(open(zip_path, 'rb'), filename=f"Карточки преподавателей {request.user.prepod.first().kafedra.name} {datetime.now().strftime('%d.%m.%Y')}.zip")


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
