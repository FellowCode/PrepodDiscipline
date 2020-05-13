from django.template.defaulttags import URLNode
from django import template
from django.template.base import TemplateSyntaxError
from utils.shortcuts import build_url

register = template.Library()


@register.simple_tag(takes_context=True)
def iurl(context, viewname, **kwargs):
    """example: 'groups:delete' signed_pk='nullable:selectedGroup.signed_pk get_prepod='prepod.id'"""
    get = {}
    delete_keys = []
    for key, dots_var in kwargs.items():
        # parse params
        if ':' in dots_var:
            dots_var = dots_var.split(':')
            params = dots_var[:-1]
            dots_var = dots_var[-1]
        else:
            params = []

        if 'nullable' in params:
            value = get_value_from_context(context, dots_var, nullable=True)
        else:
            value = get_value_from_context(context, dots_var, nullable=False)

        if 'get' in key:
            delete_keys.append(key)
            if value:
                get_key = key.split('_')[1]
                get[get_key] = value
        elif value:
            kwargs[key] = value
        else:
            kwargs[key] = 'None'

    for key in delete_keys:
        del kwargs[key]

    return build_url(viewname, **kwargs, get=get)


@register.simple_tag(takes_context=True)
def cookie(context, cookie_name):
    request = context['request']
    result = request.COOKIES.get(cookie_name, '')
    return result


def get_value_from_context(context, dots_var, nullable=False):
    c_key = dots_var.split('.')[0]
    try:
        var = context[c_key]
    except KeyError:
        if nullable:
            return None
        raise KeyError('Template context does not exist key: {}'.format(c_key))

    splitted_var = dots_var.split('.')
    if len(splitted_var) > 0:
        attr = '.'.join(splitted_var[1:])
        try:
            value = getattr(var, attr)
        except Exception:
            if nullable:
                return None
            raise AttributeError('Variable {} does not contain attribute {}'.format(splitted_var[0], attr))
    else:
        value = var

    if callable(value):
        value = value()

    return value
