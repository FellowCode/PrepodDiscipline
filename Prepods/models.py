from django.db import models
from utils.model_manager import MyManager
from Accounts.models import User

class Dolzhnost(models.Model):
    objects = MyManager()

    name = models.CharField(max_length=64, unique=True)

    class Meta:
        verbose_name_plural = "Должности"
        verbose_name = "Должность"

    def __str__(self):
        return self.name

class Prepod(models.Model):
    objects = MyManager()

    DOLZHNOST = [('Зав. кафедрой', 'Зав. кафедрой'), ('Декан', 'Декан'), ('Профессор', 'Профессор'), ('Доцент', 'Доцент'), ('Ст. преподаватель', 'Ст. преподаватель'), ('Ассистент', 'Ассистент')]

    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, related_name='prepod')

    last_name = models.CharField(max_length=64, verbose_name="Фамилия")
    first_name = models.CharField(max_length=64, verbose_name="Имя")
    surname = models.CharField(max_length=64, verbose_name="Отчество")

    #dolzhnost = models.ForeignKey(Dolzhnost, on_delete=models.SET_NULL, null=True, verbose_name="Должность")
    dolzhnost = models.CharField(choices=DOLZHNOST, max_length=64, default='Зав. кафедрой')

    kv_uroven = models.IntegerField(verbose_name="Кв. уровень")

    chasov_stavki = models.IntegerField(verbose_name="Часов ставки")

    class Meta:
        verbose_name = 'Преподаватель'
        verbose_name_plural = 'Преподаватели'

        ordering = ['last_name']

    def dolzhnost_name(self):
        return self.dolzhnost.name

    def fio(self):
        return self.__str__()

    def __str__(self):
        return f'{self.last_name} {self.first_name[0]}.{self.surname[0]}.'
