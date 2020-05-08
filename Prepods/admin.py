from django.contrib import admin

from .models import *

@admin.register(Dolzhnost)
class DolzhnostAdmin(admin.ModelAdmin):
    pass

@admin.register(Prepod)
class PrepodAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'dolzhnost_name', 'kv_uroven', 'chasov_stavki']