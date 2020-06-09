from django.contrib import admin
from django.urls import path, include
from .views import *

urlpatterns = [
    path('list/', prepods_list, name='list'),
    path('prepod-form/<id>/', prepod_form, name='prepod_form_id'),
    path('prepod-form/', prepod_form, name='prepod_form'),
    path('<id>/disciplines/', prepod_disciplines, name='disciplines'),
    path('cart/download/', prep_cart_download, name='cart_download'),
    path('cart/download-all/', download_prepod_karts, name='download_prepod_karts'),
#    path('<id>/available', prepod_available, name='available'),
    # path('upload/', disciplines_upload, name='upload'),
    # path('download/', disciplines_download, name='download')
]