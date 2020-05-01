from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist
import urllib
from django.shortcuts import reverse, redirect
import hashlib
from django.db import connection, reset_queries
from itertools import chain


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