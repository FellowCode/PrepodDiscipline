from django.contrib import admin
from django.urls import path, include
from .views import *

urlpatterns = [
    path('download-shtat-rasp/', download_shtatnoe_raspisanie, name='download_shtat_rasp'),
    path('', index, name='index'),

]
