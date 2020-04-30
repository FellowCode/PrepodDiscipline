from django.contrib import admin
from django.urls import path, include
from .views import *

urlpatterns = [
    path('list/', disciplines_list, name='list'),
    path('upload/', disciplines_upload, name='upload')
]