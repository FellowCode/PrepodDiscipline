from django.contrib import admin

from .models import *

@admin.register(Potok)
class PotokAdmin(admin.ModelAdmin):
    pass

@admin.register(DisciplineForm)
class DisciplineFormAdmin(admin.ModelAdmin):
    pass

@admin.register(Fakultet)
class FakultetAdmin(admin.ModelAdmin):
    pass

@admin.register(Specialnost)
class SpecialnostAdmin(admin.ModelAdmin):
    pass

@admin.register(Kafedra)
class KafedraAdmin(admin.ModelAdmin):
    pass

@admin.register(Discipline)
class DisciplineAdmin(admin.ModelAdmin):
    list_display = ['code', 'form', 'shifr', 'name', 'fakultet', 'specialnost']
    list_display_links = ['name']
