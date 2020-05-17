from django.contrib import admin
from django.urls import path, include
from .views import *

urlpatterns = [
    path('list/', disciplines_list, name='list'),
    path('upload/', disciplines_upload, name='upload'),
    path('download/', disciplines_download, name='download'),
    path('<dis_id>/nagruzka/', discipline_nagruzka, name='nagruzka'),
    path('<dis_id>/nagruzka/save/', save_nagruzka, name='save_nagruzka'),
    path('<dis_id>/nagruzka/edit/', edit_nagruzka, name='edit_nagruzka'),
    path('<dis_id>/nagruzka/archiving/', archiving, name='archiving'),
    path('raspred-stavok/save/', raspred_stavok_save, name='raspred_stavok_save'),
    path('raspred-stavok/', raspred_stavok, name='raspred_stavok'),

]
