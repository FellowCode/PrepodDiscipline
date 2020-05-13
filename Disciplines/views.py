from django.http import HttpResponse, JsonResponse, Http404
from django.shortcuts import render, reverse, redirect
from .models import Discipline, Nagruzka, Archive
from Prepods.models import Prepod

from utils.xls import handle_upload_disciplines, create_disciplines_xls


def disciplines_list(request):
    def get_prepod_disciplines(prepod):
        nagruzki = Nagruzka.objects.filter(prepod=prepod).all()
        dis_ids = []
        for nagruzka in nagruzki:
            if not nagruzka.archive:
                dis_ids.append(nagruzka.discipline.id)
        return Discipline.objects.filter(id__in=dis_ids)

    if not request.user.is_authenticated:
        return Http404
    if request.user.is_superuser or request.user.prepod.dolzhnost == 'Зав. кафедрой' or request.user.prepod.prava == 'raspred':
        prepod_id = request.GET.get('prepod')
        prepod = Prepod.objects.get_or_none(id=prepod_id)
        if prepod:
            disciplines = get_prepod_disciplines(prepod)
        else:
            disciplines = Discipline.objects.all()
        if not request.user.is_superuser:
            disciplines.filter(kafedra=request.user.prepod.kafedra).all()
    elif request.user.prepod:
        prepod = request.user.prepod
        if request.user.prepod.prava == 'prosmotr':
            disciplines = Discipline.objects.filter(kafedra=request.user.prepod.kafedra).all()
        else:
            disciplines = get_prepod_disciplines(prepod)
    else:
        raise Http404
    return render(request, 'Disciplines/List.html', {'disciplines': disciplines, 'prepod': prepod})


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

    dis = Discipline.objects.get_or_404(id=dis_id)
    prepods = Prepod.objects.all()
    nagruzki = Nagruzka.objects.filter(discipline=dis, archive=None).all()
    archives = Archive.objects.filter(discipline=dis).all()

    editable = request.user.is_superuser or request.user.prepod == 'Зав. кафедрой' or request.user.prepod.prava == 'raspred'

    return render(request, 'Disciplines/Nagruzka.html',
                  {'dis': dis, 'prepods': prepods, 'nagruzki': nagruzki, 'editable': editable, 'archives': archives})


def save_nagruzka(request, dis_id):
    if not request.user.is_superuser or not request.is_ajax() or not request.method == 'POST':
        raise Http404

    dis = Discipline.objects.get_or_404(id=dis_id)

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
        Nagruzka(**nagruzka).save()
        i += 1
    return JsonResponse({'status': 'OK'})

def edit_nagruzka(request, dis_id):
    if not request.user.is_superuser:
        raise Http404
    dis = Discipline.objects.get_or_404(id=dis_id)
    nagruzka_ids = request.POST.getlist('nagruzka_id')
    prepod_ids = request.POST.getlist('prepod')

    archive = Archive(discipline=dis)
    archive.save()

    nagruzki = Nagruzka.objects.filter(discipline=dis, archive=None).all()
    for nagruzka in nagruzki:
        nagruzka.archive = archive
        nagruzka.save()
        index = nagruzka_ids.index(str(nagruzka.id))
        nagruzka.pk = None
        nagruzka.archive = None
        nagruzka.prepod = Prepod.objects.get(id=prepod_ids[index])
        nagruzka.save()

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
