from django.template.defaulttags import URLNode
from django import template
from django.template.base import TemplateSyntaxError
from utils.shortcuts import build_url

register = template.Library()
