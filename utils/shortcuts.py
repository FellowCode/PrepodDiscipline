from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist
import urllib

from django.db.models import Count, Q, Sum
from django.shortcuts import reverse, redirect
import hashlib
from django.db import connection, reset_queries
from itertools import chain

from Disciplines.models import Discipline, Nagruzka


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


def check_discipline_errors(request):
    dis_errors = True
    if request.user.is_superuser:
        dis_errors = len(Discipline.objects.filter(errors=True).all()) > 0
        dis_errors = dis_errors or Discipline.objects.annotate(
            num_nagruzki=Count('nagruzki', filter=Q(nagruzki__archive=None))).filter(
            num_nagruzki__lte=0).count() > 0
    elif request.user.is_authenticated and request.user.prepod.count() > 0:
        dis_errors = len(Discipline.objects.filter(errors=True, kafedra=request.user.prepod.first().kafedra).all()) > 0
        dis_errors = dis_errors or Discipline.objects.filter(kafedra=request.user.prepod.first().kafedra).annotate(
            num_nagruzki=Count('nagruzki', filter=Q(nagruzki__archive=None))).filter(
            num_nagruzki__lte=0).count() > 0
    return dis_errors


def get_group_nagruzki(request, vne_budget):
    if vne_budget:
        nagruzki = Nagruzka.objects.filter(archive=None, discipline__form__name__contains='_В')
    else:
        nagruzki = Nagruzka.objects.filter(archive=None).exclude(discipline__form__name__contains='_В').all()
    if not request.user.is_superuser:
        nagruzki = nagruzki.filter(discipline__kafedra=request.user.prepod.first().kafedra)
    group_nagruzki = nagruzki.values('prepod__id', 'prepod__fio', 'prepod__dolzhnost',
                                     'prepod__kv_uroven', 'prepod__pkgd', 'prepod__uch_stepen', 'prepod__uch_zvanie',
                                     'prepod__srok_izbr', 'prepod__dogovor', 'n_stavka', 'pochasovka',
                                     'prepod__chasov_stavki').order_by('prepod__fio') \
        .order_by('-prepod__kv_uroven', 'prepod__fio').annotate(Sum('summary'))
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
            group_nagruzki_budget[key]['vnebudget_p_stavka'] = vnebudget.get('pochas_stavka')
            group_nagruzki_budget[key]['sum_p_vnebudget'] = vnebudget['sum_p']
            group_nagruzki_budget[key].pop('pochasovka')
    group_nagruzki = group_nagruzki_budget
    for key, nagruzka in group_nagruzki_vnebudget.items():
        nagruzka.pop('pochasovka')
        group_nagruzki[key] = nagruzka
        group_nagruzki[key]['vnebudget_stavka'] = nagruzka['n_stavka']
        group_nagruzki[key]['vnebudget_p_stavka'] = nagruzka.get('pochas_stavka')
        group_nagruzki[key]['sum_p_vnebudget'] = nagruzka['sum_p']
        group_nagruzki[key]['n_stavka'] = None
        group_nagruzki[key]['pochas_stavka'] = None
        group_nagruzki[key]['sum_p'] = None
    return group_nagruzki
