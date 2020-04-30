from django.contrib import admin

from Accounts.models import User
from django.contrib.auth.models import Group

admin.site.unregister(Group)

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    def create_date(self, obj):
        return obj.date_joined.strftime("%d.%m.%Y")

    create_date.admin_order_field = 'date_joined'
    create_date.short_description = 'Дата регистрации'

    def _last_login(self, obj):
        if obj.last_login:
            return obj.last_login.strftime("%d.%m.%Y %H:%M:%S")
        return None

    _last_login.admin_order_field = 'last_login'
    _last_login.short_description = 'Дата авторизации'

    @staticmethod
    def _mail_dt(obj):
        if obj.mail_dt:
            return obj.mail_dt.strftime("%d.%m.%Y %H:%M:%S")
        return None

    list_display = ['id', 'email', 'create_date', '_last_login', 'is_confirm']
    list_filter = ['is_confirm']

    list_display_links = ['email']

    readonly_fields = ['password', '_last_login', 'create_date', '_mail_dt']
    exclude = ['last_login', 'date_joined', 'mail_dt', 'groups', 'user_permissions']