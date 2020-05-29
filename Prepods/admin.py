from django.contrib import admin
from django.shortcuts import redirect
from django.urls import reverse

from .models import *

@admin.register(Prepod)
class PrepodAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'dolzhnost', 'kv_uroven', 'chasov_stavki']
    fields = ['user', 'last_name', 'first_name', 'surname', 'dolzhnost', 'kafedra', 'kv_uroven', 'chasov_stavki', 'prava']

    # def has_delete_permission(self, request, obj=None):
    #
    #     if hasattr(request.user, 'prepod') and request.user.prepod.dolzhnost == 'Зав. кафедрой':
    #         return True
    #     return super(PrepodAdmin, self).has_delete_permission(request)
    #
    # def has_view_or_change_permission(self, request, obj=None):
    #     if hasattr(request.user, 'prepod') and request.user.prepod.dolzhnost == 'Зав. кафедрой':
    #         return True
    #     # If a user is not a teacher, let Django evaluate their specific permissions (a superusuer will always have permission if you do it this way)
    #     return super(PrepodAdmin, self).has_view_or_change_permission(request, obj=obj)
    #
    # def has_change_permission(self, request, obj=None):
    #     if hasattr(request.user, 'prepod') and request.user.prepod.dolzhnost == 'Зав. кафедрой':
    #         return True
    #     # If a user is not a teacher, let Django evaluate their specific permissions (a superusuer will always have permission if you do it this way)
    #     return super(PrepodAdmin, self).has_change_permission(request, obj=obj)
    #
    # def has_add_permission(self, request):
    #     if hasattr(request.user, 'prepod') and request.user.prepod.dolzhnost == 'Зав. кафедрой':
    #         return True
    #     return super(PrepodAdmin, self).has_add_permission(request)