import operator
from functools import reduce

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse, Http404, FileResponse
from django.shortcuts import render, reverse, redirect

from utils.decorators import prepod_only
from utils.shortcuts import get_group_nagruzki, get_shtat_rasp, iredirect
from utils.word import word_shtat_rasp
from .models import Discipline, Nagruzka, Archive, Fakultet
from Prepods.models import Prepod

from utils.xls import handle_upload_disciplines, create_disciplines_xls, excel_shtat_rasp
from utils import xls


@login_required
@prepod_only
def disciplines_list(request):
    def get_prepods_disciplines(prepods):
        disciplines = Discipline.objects.none()
        for prepod in prepods:
            disciplines = disciplines.union(get_prepod_disciplines(prepod))
        return disciplines

    def get_prepod_disciplines(prepod):
        nagruzki = Nagruzka.objects.filter(prepod=prepod).all()
        dis_ids = []
        for nagruzka in nagruzki:
            if not nagruzka.archive and hasattr(nagruzka, 'discipline') and hasattr(nagruzka.discipline, 'id'):
                dis_ids.append(nagruzka.discipline.id)
        return Discipline.objects.filter(id__in=dis_ids)

    if not request.user.is_authenticated:
        return Http404
    raspred = False
    zav_kafedra = False
    prosmotr = False
    for prepod in request.user.prepod.all():
        raspred = raspred or prepod.prava == 'raspred'
        prosmotr = raspred or prepod.prava == 'prosmotr'
        zav_kafedra = zav_kafedra or prepod.dolzhnost == 'Зав. кафедрой'
    if request.user.is_superuser or zav_kafedra or raspred:
        prepod_id = request.GET.get('prepod')
        prepod = Prepod.objects.get_or_none(id=prepod_id)
        if prepod:
            if prepod.user:
                disciplines = get_prepods_disciplines(prepod.user.prepod.all())
            else:
                disciplines = get_prepod_disciplines(prepod)
        else:
            disciplines = Discipline.objects.all()
        if not request.user.is_superuser:
            disciplines = disciplines.filter(kafedra=request.user.prepod.first().kafedra).all()
    elif request.user.prepod.count() > 0:
        prepod = request.user.prepod.first()
        if prosmotr:
            disciplines = Discipline.objects.filter(kafedra=request.user.prepod.first().kafedra).all()
        else:
            disciplines = get_prepods_disciplines(request.user.prepod.all())
    else:
        raise Http404
    search = request.GET.get('search')
    if search:
        search_qs = reduce(operator.or_, (Q(name__icontains=x) for x in search.split(' ')))
        disciplines = disciplines.filter(search_qs)

    PER_PAGE = 150
    page = int(request.GET.get('page', '1'))
    pages = disciplines.count() // PER_PAGE
    disciplines = disciplines[PER_PAGE * (page - 1):PER_PAGE * (page)]

    disciplines = disciplines.prefetch_related('nagruzki')

    return render(request, 'Disciplines/List.html',
                  {'disciplines': disciplines, 'prepod': prepod,
                   'parse_progress': xls.upload_progress, 'parsing': xls.parsing, 'page': page,
                   'pages': range(pages + 1), 'offset': PER_PAGE * (page - 1), 'search': search})


@login_required
@prepod_only
def disciplines_upload(request):
    if request.user.is_superuser and request.is_ajax() and request.method == 'POST':
        handle_upload_disciplines(request.FILES['disciplines'], request.POST.get('action'))
        return JsonResponse({'status': 'OK'})
    raise Http404


@login_required
@prepod_only
def parse_progress(request):
    if request.is_ajax():
        return JsonResponse({'status': xls.parsing, 'progress': xls.upload_progress})


@login_required
@prepod_only
def disciplines_download(request):
    if request.is_ajax() and request.method == 'POST':
        create_disciplines_xls()
        return JsonResponse({'status': 'OK'})
    raise Http404


@login_required
@prepod_only
def discipline_nagruzka(request, dis_id):
    dis = Discipline.objects.get_or_404(id=dis_id)
    dis.check_nagruzka_sum()
    prepods = Prepod.objects.filter(kafedra=dis.kafedra)
    nagruzki = Nagruzka.objects.filter(discipline=dis, archive=None).all()
    archives = Archive.objects.filter(discipline=dis).all()

    editable = request.user.is_superuser or request.user.is_zav_kafedra() or request.user.raspred()

    data = {'dis': dis, 'prepods': prepods, 'nagruzki': nagruzki, 'editable': editable, 'archives': archives,
            'edit': request.GET.get('edit'), 'stavka_range': stavka_range(), 'errors': dis.check_nagruzka_sum(),
            'source_page': request.GET.get('source_page', 1)}

    return render(request, 'Disciplines/Nagruzka.html', data)


def stavka_range():
    return [round(x * 0.05, 2) for x in range(21)]


@login_required
@prepod_only
def save_nagruzka(request, dis_id):
    dis = Discipline.objects.get_or_404(id=dis_id)

    CELL_NAMES = ['prepod', 'n_stavka', 'pochasovka', 'student', 'lk', 'pr', 'lr', 'k_tek', 'k_ekz', 'zachet',
                  'ekzamen', 'kontr_raboti', 'kr_kp',
                  'vkr',
                  'pr_ped', 'pr_dr', 'gak', 'aspirantura', 'rukovodstvo', 'dop_chasi']

    nagruzki = Nagruzka.objects.filter(discipline=dis, archive=None).all()
    if len(nagruzki) > 0:
        archive = Archive(discipline=dis)
        archive.save()
        for nagruzka in nagruzki:
            nagruzka.archive = archive
            nagruzka.save()

    i = 0
    while i < len(request.POST.getlist('student', [])):
        nagruzka = {'discipline': dis}
        for cell_name in CELL_NAMES:
            nagruzka[cell_name] = request.POST.getlist(cell_name, [])[i].replace(',', '.')
            if cell_name == 'prepod':
                nagruzka[cell_name] = Prepod.objects.get(id=nagruzka[cell_name])
            if cell_name == 'pochasovka':
                nagruzka[cell_name] = nagruzka[cell_name].lower() == 'true'
        Nagruzka(**nagruzka).save()
        i += 1
    dis.check_nagruzka_sum()
    dis.save()
    return JsonResponse({'status': 'OK'})


@login_required
@prepod_only
def edit_nagruzka(request, dis_id):
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


@login_required
@prepod_only
def archiving(request, dis_id):
    dis = Discipline.objects.get_or_404(id=dis_id)

    nagruzki = Nagruzka.objects.filter(discipline=dis, archive=None).all()

    archive = Archive(discipline=dis)
    archive.save()

    nagruzki.update(archive=archive)
    Nagruzka.objects.bulk_update(nagruzki, ['archive'])

    dis.check_nagruzka_sum()
    dis.save()

    return redirect(f"/disciplines/{dis.id}/nagruzka/?source_page={request.GET.get('source_page', 1)}")


from django.db.models import Sum, Q


@login_required
@prepod_only
def raspred_stavok(request):
    vne_budget = request.GET.get('vne_budget')
    group_nagruzki = get_group_nagruzki(request, vne_budget)

    return render(request, 'Disciplines/RaspredStavok.html',
                  {'group_nagruzki': group_nagruzki, 'stavka_range': stavka_range, 'vne_budget': vne_budget})


@login_required
@prepod_only
def raspred_stavok_save(request):
    filter = request.POST.dict()
    filter.pop('csrfmiddlewaretoken')
    filter['pochasovka'] = filter['pochasovka'].lower() == 'true'
    filter['n_stavka'] = filter['n_stavka'].replace(',', '.')
    update = {'n_stavka': filter.pop('n_stavka_new').replace(',', '.')}
    if 'pochasovka_new' in filter:
        update['pochasovka'] = True
        filter.pop('pochasovka_new')
    else:
        update['pochasovka'] = False
    vne_budget = filter.pop('vne_budget') != 'None'
    if vne_budget:
        nagruzki = Nagruzka.objects.filter(archive=None, discipline__form__name__contains='_В').all()
    else:
        nagruzki = Nagruzka.objects.filter(archive=None).exclude(discipline__form__name__contains='_В').all()
    if not request.user.is_superuser:
        nagruzki = nagruzki.filter(discipline__kafedra=request.user.prepod.first().kafedra)
    nagruzki.filter(**filter).update(**update)

    return redirect(reverse('disciplines:raspred_stavok'))


@login_required
@prepod_only
def shtat_raspisanie(request):
    if request.GET.get('fakultet', '') != '':
        cur_fakultet = Fakultet.objects.get_or_none(id=request.GET.get('fakultet'))
    else:
        cur_fakultet = None
    prepods = get_shtat_rasp(request, fakultet=cur_fakultet)
    fakultets = Fakultet.objects.all()
    return render(request, 'Disciplines/ShtatRaspisanie.html',
                  {'prepods': prepods, 'fakultets': fakultets, 'cur_fakultet': cur_fakultet})


@login_required
@prepod_only
def download_shtatnoe_raspisanie(request):
    if request.user.is_superuser or request.user.is_zav_kafedra:
        if request.GET.get('type', 'word') == 'word':
            path = word_shtat_rasp(request, fakultet_id=request.GET.get('fakultet', ''))
        elif request.GET.get('type', 'word') == 'excel':
            path = excel_shtat_rasp(request, fakultet_id=request.GET.get('fakultet', ''))
        else:
            path = excel_shtat_rasp(request, fakultet_id=request.GET.get('fakultet', ''), _all=True)
        return FileResponse(open(path, 'rb'))
    return iredirect('main:index')
