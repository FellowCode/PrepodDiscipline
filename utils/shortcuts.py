from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist
import urllib

from django.db.models import Count, Q, Sum
from django.shortcuts import reverse, redirect
import hashlib
from django.db import connection, reset_queries
from itertools import chain

from Disciplines.models import Discipline, Nagruzka
from Prepods.models import Prepod


def send_mail(send_func, interval_m, last_date):
    before_send = 0

    if last_date:
        dtime = datetime.now() - last_date
        dmin = dtime.total_seconds() // 60
        if dmin > interval_m:
            if send_func:
                send_func()
        else:
            before_send = interval_m + 1 - dmin
    elif send_func:
        send_func()
    return int(before_send)


def get_or_none(model, **kwargs):
    try:
        return model.objects.get(**kwargs)
    except ObjectDoesNotExist:
        return None


def build_url(*args, **kwargs):
    get = kwargs.pop('get', {})
    url = reverse(*args, kwargs=kwargs)
    if get:
        url += '?' + urllib.parse.urlencode(get)
    return url


def iredirect(viewname, **kwargs):
    return redirect(build_url(viewname, **kwargs))


def check_hash(origin, _hash):
    o_hash = hashlib.sha256(origin.encode('utf-8')).hexdigest()
    return o_hash == _hash


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def db_queries(reset=True):
    if reset:
        reset_queries()
    return connection.queries


def obj_to_dict(instance):
    opts = instance._meta
    data = {}
    for f in chain(opts.concrete_fields, opts.private_fields):
        data[f.name] = f.value_from_object(instance)
    for f in opts.many_to_many:
        data[f.name] = [i.id for i in f.value_from_object(instance)]
    return data


def check_discipline_errors(request, fakultet=None):
    dis_errors = True
    if fakultet:
        disciplines = Discipline.objects.filter(fakultet=fakultet)
    else:
        disciplines = Discipline.objects.all()
    if request.user.is_superuser:
        dis_errors = len(Discipline.objects.filter(errors=True).all()) > 0
        dis_errors = dis_errors or disciplines.annotate(
            num_nagruzki=Count('nagruzki', filter=Q(nagruzki__archive=None))).filter(
            num_nagruzki__lte=0).count() > 0
    elif request.user.is_authenticated and request.user.prepod.count() > 0:
        if not fakultet:
            disciplines = disciplines.filter(kafedra=request.user.prepod.first().kafedra)
        dis_errors = len(Discipline.objects.filter(errors=True, kafedra=request.user.prepod.first().kafedra).all()) > 0
        dis_errors = dis_errors or disciplines.annotate(
            num_nagruzki=Count('nagruzki', filter=Q(nagruzki__archive=None))).filter(
            num_nagruzki__lte=0).count() > 0
    return dis_errors


def get_group_nagruzki(request, vne_budget, fakultet=None, _all=False):
    if vne_budget:
        nagruzki = Nagruzka.objects.filter(archive=None, discipline__form__name__contains='_В')
    else:
        nagruzki = Nagruzka.objects.filter(archive=None).exclude(discipline__form__name__contains='_В').all()
    if fakultet:
        nagruzki = nagruzki.filter(discipline__fakultet=fakultet)
    elif not request.user.is_superuser and not _all:
        nagruzki = nagruzki.filter(discipline__kafedra=request.user.prepod.first().kafedra)
    group_nagruzki = nagruzki.values('prepod__id', 'prepod__fio', 'prepod__dolzhnost',
                                     'prepod__kv_uroven', 'prepod__pkgd', 'prepod__uch_stepen', 'prepod__uch_zvanie',
                                     'prepod__srok_izbr', 'prepod__dogovor', 'n_stavka', 'pochasovka',
                                     'prepod__chasov_stavki').order_by('-prepod__kv_uroven', 'prepod__fio').annotate(Sum('summary'))
    return group_nagruzki


def annotate_pochasovka(group_nagruzki):
    group_nagruzki = list(group_nagruzki)
    new_group_nagruzki = {}
    for nagruzka in group_nagruzki:
        prepod_id = nagruzka.pop('prepod__id')
        if prepod_id in new_group_nagruzki:
            n = new_group_nagruzki[prepod_id]
        else:
            n = nagruzka
        if nagruzka['pochasovka']:
            n['pochas_stavka'] = nagruzka['n_stavka']
            n['sum_p'] = nagruzka['summary__sum']
        else:
            n['n_stavka'] = nagruzka['n_stavka']
        new_group_nagruzki[prepod_id] = n
    return new_group_nagruzki


def annotate_group_nagruzki(group_nagruzki_budget, group_nagruzki_vnebudget):
    for key, nagruzka in group_nagruzki_budget.items():
        if key in group_nagruzki_vnebudget:
            vnebudget = group_nagruzki_vnebudget.pop(key)
            group_nagruzki_budget[key]['vnebudget_stavka'] = vnebudget['n_stavka']
            group_nagruzki_budget[key]['vnebudget_p_stavka'] = vnebudget.get('pochas_stavka', 0)
            group_nagruzki_budget[key]['sum_p_vnebudget'] = vnebudget.get('sum_p', 0)
            group_nagruzki_budget[key].pop('pochasovka')
    group_nagruzki = group_nagruzki_budget
    for key, nagruzka in group_nagruzki_vnebudget.items():
        nagruzka.pop('pochasovka')
        group_nagruzki[key] = nagruzka
        group_nagruzki[key]['vnebudget_stavka'] = nagruzka['n_stavka']
        group_nagruzki[key]['vnebudget_p_stavka'] = nagruzka.get('pochas_stavka', 0)
        group_nagruzki[key]['sum_p_vnebudget'] = nagruzka.get('sum_p', 0)
        group_nagruzki[key]['n_stavka'] = 0
        group_nagruzki[key]['pochas_stavka'] = 0
        group_nagruzki[key]['sum_p'] = 0
    return group_nagruzki


def get_shtat_rasp(request, fakultet=None, _all=False):
    nagruzki_budget = get_group_nagruzki(request, vne_budget=False, fakultet=fakultet, _all=_all)
    nagruzki_budget = annotate_pochasovka(nagruzki_budget)
    nagruzki_vnebudget = get_group_nagruzki(request, vne_budget=True, fakultet=fakultet, _all=_all)
    nagruzki_vnebudget = annotate_pochasovka(nagruzki_vnebudget)
    prepods = annotate_group_nagruzki(nagruzki_budget, nagruzki_vnebudget)

    p = {'sums': {'n_stavka_sum': 0, 'n_p_stavka_sum': 0, 'n_p_ch_stavka_sum': 0, 'v_n_stavka_sum': 0,
                  'v_n_p_stavka_sum': 0, 'v_n_p_ch_stavka_sum': 0},
         'rows': {}}

    for id, prepod in prepods.items():
        p['sums']['n_stavka_sum'] += prepod.get('n_stavka', 0)
        p['sums']['n_p_stavka_sum'] += prepod.get('pochas_stavka', 0)
        p['sums']['n_p_ch_stavka_sum'] += prepod.get('sum_p', 0)
        p['sums']['v_n_stavka_sum'] += prepod.get('vnebudget_stavka', 0)
        p['sums']['v_n_p_stavka_sum'] += prepod.get('vnebudget_p_stavka', 0)
        p['sums']['v_n_p_ch_stavka_sum'] += prepod.get('sum_p_vnebudget', 0)

        r = ['']*11

        r[0] = prepod['prepod__dolzhnost']
        r[1] = Prepod.get_display_value('PKGD', prepod['prepod__pkgd'])
        r[2] = prepod['prepod__kv_uroven']
        if prepod['prepod__srok_izbr']:
            r[3] = prepod['prepod__srok_izbr'].strftime('%d.%m.%Y')
        r[4] = prepod['prepod__fio']
        st_zv = []
        if prepod['prepod__uch_stepen']:
            st_zv.append(prepod['prepod__uch_stepen'])
        if prepod['prepod__uch_zvanie']:
            st_zv.append(Prepod.get_display_value('UCH_ZVANIE', prepod['prepod__uch_zvanie']))
        r[5] = ', '.join(st_zv)
        if prepod['prepod__dogovor']:
            r[6] = 'Договор'
        if prepod.get('n_stavka') and prepod['n_stavka'] > 0:
            r[7] = prepod['n_stavka']
        if prepod.get('pochas_stavka') and prepod['pochas_stavka'] > 0:
            r[8] = f"{prepod['pochas_stavka']}\n({prepod.get('sum_p', 0)})"
        if prepod.get('vnebudget_stavka') and prepod['vnebudget_stavka'] > 0:
            r[9] = prepod['vnebudget_stavka']
        if prepod.get('vnebudget_p_stavka') and prepod['vnebudget_p_stavka'] > 0:
            r[10] = f"{prepod['vnebudget_p_stavka']}\n({prepod.get('sum_p_vnebudget', 0)})"
        p['rows'][id] = r

    p['sums']['b_stavka'] = p['sums']['n_stavka_sum'] + p['sums']['n_p_stavka_sum']
    p['sums']['v_stavka'] = p['sums']['v_n_stavka_sum'] + p['sums']['v_n_p_stavka_sum']
    p['sums']['stavka'] = p['sums']['b_stavka'] + p['sums']['v_stavka']

    return p


def create_otchet_archive():
    pass