from django.db import models
from utils.model_manager import MyManager
from Accounts.models import User

class Prepod(models.Model):
    objects = MyManager()

    DOLZHNOST = [('Зав. кафедрой', 'Зав. кафедрой'), ('Декан', 'Декан'), ('Профессор', 'Профессор'), ('Доцент', 'Доцент'), ('Ст. преподаватель', 'Ст. преподаватель'), ('Ассистент', 'Ассистент')]

    PRAVA = [('raspred', 'Распределение и просмотр'), ('prosmotr', 'Только просмотр по кафедре'), ('None', 'Просмотр своих дисциплин')]

    PKGD = [('pps', 'ППС')]

    UCH_ZVANIE = [('docent', 'доцент'), ('prof', 'профессор'), ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='prepod', blank=True)

    email = models.EmailField(verbose_name='Email', null=True)

    last_name = models.CharField(max_length=64, verbose_name="Фамилия")
    first_name = models.CharField(max_length=64, verbose_name="Имя")
    surname = models.CharField(max_length=64, verbose_name="Отчество")

    fio = models.CharField(max_length=256, verbose_name='ФИО', blank=True, default='')

    dolzhnost = models.CharField(choices=DOLZHNOST, max_length=64, default='Зав. кафедрой')

    kafedra = models.ForeignKey('Disciplines.Kafedra', on_delete=models.SET_NULL, null=True, default=None, blank=True)

    kv_uroven = models.IntegerField(verbose_name="Кв. уровень")

    chasov_stavki = models.IntegerField(verbose_name="Часов ставки")

    pkgd = models.CharField(max_length=32, choices=PKGD, default='pps')

    srok_izbr = models.DateField(null=True)
    uch_stepen = models.CharField(max_length=32, null=True, blank=True)
    uch_zvanie = models.CharField(max_length=32, choices=UCH_ZVANIE, null=True, blank=True)

    dogovor = models.BooleanField(default=False)

    prava = models.CharField(max_length=128, choices=PRAVA, default='None', verbose_name='Права')

    def save(self, **kwargs):
        self.fio = self.get_fio()
        if self.user and not self.user.is_superuser:
            self.user.is_staff = False
            self.user.save()

        self.user = User.objects.get_or_none(email=self.email)
        if self.dolzhnost == 'Зав. кафедрой':
            self.prava = 'raspred'
            if self.user and not self.user.is_superuser:
                self.user.is_staff = True
                self.user.save()
        elif self.user and not self.user.is_superuser:
            self.user.is_staff = False
            self.user.save()

        super().save(**kwargs)

    class Meta:
        verbose_name = 'Преподаватель'
        verbose_name_plural = 'Преподаватели'

        ordering = ['last_name']

    def dolzhnost_name(self):
        return self.dolzhnost

    def get_fio(self):
        return f'{self.last_name} {self.first_name[0]}.{self.surname[0]}.'

    def __str__(self):
        return self.get_fio()

    @classmethod
    def get_display_value(cls, choices_name, field_val):
        choices = eval(f'cls.{choices_name}')
        for key, val in choices:
            if key == field_val:
                return val
