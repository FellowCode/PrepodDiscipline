from django.db import models
from utils.model_manager import MyManager
from Accounts.models import User


class Prepod(models.Model):
    objects = MyManager()

    DOLZHNOST = [('Зав. кафедрой', 'Зав. кафедрой'), ('Декан', 'Декан'), ('Профессор', 'Профессор'), ('Доцент', 'Доцент'), ('Ст. преподаватель', 'Ст. преподаватель'), ('Ассистент', 'Ассистент')]

    PRAVA = [('raspred', 'Распределение и просмотр'), ('prosmotr', 'Только просмотр по кафедре'), (None, 'Просмотр своих дисциплин')]

    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, related_name='prepod', blank=True)

    last_name = models.CharField(max_length=64, verbose_name="Фамилия")
    first_name = models.CharField(max_length=64, verbose_name="Имя")
    surname = models.CharField(max_length=64, verbose_name="Отчество")

    dolzhnost = models.CharField(choices=DOLZHNOST, max_length=64, default='Зав. кафедрой')

    kafedra = models.ForeignKey('Disciplines.Kafedra', on_delete=models.SET_NULL, null=True, default=None, blank=True)

    kv_uroven = models.IntegerField(verbose_name="Кв. уровень")

    chasov_stavki = models.IntegerField(verbose_name="Часов ставки")

    prava = models.CharField(max_length=128, choices=PRAVA, default=None, verbose_name='Права', null=True, blank=True)

    def save(self, **kwargs):
        if self.dolzhnost == 'Зав. кафедрой':
            self.prava = 'raspred'
            if self.user:
                self.user.is_staff = True
                self.user.save()
        else:
            if self.user:
                self.user.is_staff = False
                self.user.save()
        super().save(**kwargs)

    class Meta:
        verbose_name = 'Преподаватель'
        verbose_name_plural = 'Преподаватели'

        ordering = ['last_name']

    def dolzhnost_name(self):
        return self.dolzhnost

    def fio(self):
        return self.__str__()

    def __str__(self):
        return f'{self.last_name} {self.first_name[0]}.{self.surname[0]}.'
