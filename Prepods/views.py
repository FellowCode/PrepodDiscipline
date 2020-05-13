from django.db.models import F
from django.http import JsonResponse, Http404
from django.shortcuts import render

from Prepods.models import Prepod
from Disciplines.models import Discipline

from utils.xls import create_prep_ds_xls

def prepods_list(request):
    return render(request, 'Prepods/List.html', {'prepods': Prepod.objects.all()})

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

def prep_ds_download(request, id):
    prepod = Prepod.objects.get_or_404(id=id)
    if request.is_ajax() and request.method == 'POST' and (request.user.is_superuser or request.user.prepod == prepod):
        url, filename = create_prep_ds_xls(prepod)
        return JsonResponse({'status': 'OK', 'url': url, 'filename': filename})
    raise Http404