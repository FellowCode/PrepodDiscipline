from django.template.base import TemplateSyntaxError
from utils.shortcuts import build_url
from django import template

register = template.Library()

@register.filter
def yes_no(val):
    if val:
        return 'Да'
    else:
        return 'Нет'


@register.filter
def div(val1, val2):
    return round(val1/val2, 2)

