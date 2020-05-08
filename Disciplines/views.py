from django.http import HttpResponse, JsonResponse, Http404
from django.shortcuts import render, reverse, redirect
from .models import Discipline, Nagruzka, Archive
from Prepods.models import Prepod

from utils.xls import handle_upload_disciplines, create_disciplines_xls


def disciplines_list(request):
    disciplines = Discipline.objects.all()
    return render(request, 'Disciplines/List.html', {'disciplines': disciplines})


def disciplines_upload(request):
    if request.user.is_superuser and request.is_ajax() and request.method == 'POST':
        handle_upload_disciplines(request.FILES['disciplines'], request.POST.get('action'))
        return JsonResponse({'status': 'OK'})
    raise Http404


def disciplines_download(request):
    if request.is_ajax() and request.method == 'POST':
        create_disciplines_xls()
        return JsonResponse({'status': 'OK'})
    raise Http404


def discipline_nagruzka(request, dis_id):
    if not request.user.is_superuser:
        raise Http404

    dis = Discipline.objects.get_or_404(id=dis_id)
    prepods = Prepod.objects.all()
    nagruzki = Nagruzka.objects.filter(discipline=dis, archive=None).all()
    archives = Archive.objects.filter(discipline=dis).all()

    return render(request, 'Disciplines/Nagruzka.html',
                  {'dis': dis, 'prepods': prepods, 'nagruzki': nagruzki, 'archives': archives})


def save_nagruzka(request, dis_id):
    if not request.user.is_superuser or not request.is_ajax() or not request.method == 'POST':
        raise Http404

    dis = Discipline.objects.get_or_404(id=dis_id)
    prepods = Prepod.objects.all()

    CELL_NAMES = ['prepod', 'student', 'lk', 'pr', 'lr', 'k_tek', 'k_ekz', 'zachet', 'ekzamen', 'kontr_raboti', 'kr_kp',
                  'vkr',
                  'pr_ped', 'pr_dr', 'gak', 'aspirantura', 'rukovodstvo', 'dop_chasi']

    i = 0
    while i < len(request.POST.getlist('student', [])):
        nagruzka = {'discipline': dis}
        for cell_name in CELL_NAMES:
            nagruzka[cell_name] = request.POST.getlist(cell_name, [])[i].replace(',', '.')
            if cell_name == 'prepod':
                nagruzka[cell_name] = Prepod.objects.get(id=nagruzka[cell_name])
        print(nagruzka)
        Nagruzka(**nagruzka).save()
        i += 1
    return JsonResponse({'status': 'OK'})


def archiving(request, dis_id):
    if not request.user.is_superuser:
        raise Http404

    dis = Discipline.objects.get_or_404(id=dis_id)
    nagruzki = Nagruzka.objects.filter(discipline=dis, archive=None).all()

    archive = Archive(discipline=dis)
    archive.save()

    nagruzki.update(archive=archive)
    Nagruzka.objects.bulk_update(nagruzki, ['archive'])

    return redirect(f'/disciplines/{dis.id}/nagruzka/')
