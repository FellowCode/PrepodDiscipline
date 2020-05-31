from django.contrib import admin

from .models import *


@admin.register(Potok)
class PotokAdmin(admin.ModelAdmin):
    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(DisciplineForm)
class DisciplineFormAdmin(admin.ModelAdmin):
    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Fakultet)
class FakultetAdmin(admin.ModelAdmin):
    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Specialnost)
class SpecialnostAdmin(admin.ModelAdmin):
    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Kafedra)
class KafedraAdmin(admin.ModelAdmin):
    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Nagruzka)
class NagruzkaAdmin(admin.ModelAdmin):
    pass

class NagruzkaInline(admin.TabularInline):
    model = Nagruzka
    extra = 0

@admin.register(Archive)
class ArchiveAdmin(admin.ModelAdmin):
    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    readonly_fields = ['dt']

    inlines = [NagruzkaInline]

    def get_discipline(self, obj):
        return obj.discipline.name

    get_discipline.short_description = 'Дисциплина'
    get_discipline.admin_order_field = 'discipline__name'

    list_display = ['get_discipline', 'dt']

class ArchiveInline(admin.TabularInline):
    model = Archive
    extra = 0




@admin.register(Discipline)
class DisciplineAdmin(admin.ModelAdmin):
    change_form_template = 'admin/change_form_discipline.html'

    list_display = ['code', 'form', 'shifr', 'name', 'fakultet', 'specialnost']
    list_display_links = ['name']

    readonly_fields = ['code', 'form', 'shifr', 'name', 'fakultet', 'specialnost', 'kurs', 'semestr', 'period',
                       'nedeli',
                       'trudoemkost', 'chas_v_nedelu', 'srs', 'chas_po_planu', 'student', 'group', 'podgroup', 'lk',
                       'pr',
                       'lr', 'k_tek', 'k_ekz', 'zachet', 'ekzamen', 'kontr_raboti', 'kr_kp', 'vkr', 'pr_ped', 'pr_dr',
                       'gak',
                       'aspirantura', 'rukovodstvo', 'dop_chasi', 'summary', 'kafedra', 'potok']

    inlines = [NagruzkaInline, ArchiveInline]
