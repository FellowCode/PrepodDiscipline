from django.contrib import admin
from django.urls import path, include
from .views import *

urlpatterns = [
    path('list/', prepods_list, name='list'),
    path('<id>/disciplines', prepod_disciplines, name='disciplines'),
    path('<id>/available', prepod_available, name='available'),
    # path('upload/', disciplines_upload, name='upload'),
    # path('download/', disciplines_download, name='download')
]