from django.db import models
from utils.model_manager import MyManager


class DisciplineForm(models.Model):
    name = models.CharField(max_length=16, unique=True)

    class Meta:
        verbose_name = 'Форма дисциплины'
        verbose_name_plural = 'Формы дисциплины'


class Fakultet(models.Model):
    name = models.CharField(max_length=16, unique=True)

    class Meta:
        verbose_name = 'Факультет'
        verbose_name_plural = 'Факультеты'


class Specialnost(models.Model):
    name = models.CharField(max_length=16, unique=True)

    class Meta:
        verbose_name = 'Специальность'
        verbose_name_plural = 'Специальности'


class Kafedra(models.Model):
    name = models.CharField(max_length=16, unique=True)

    class Meta:
        verbose_name = 'Кафедра'
        verbose_name_plural = 'Кафедры'


class Potok(models.Model):
    name = models.CharField(max_length=128, unique=True)

    class Meta:
        verbose_name = 'Поток'
        verbose_name_plural = 'Потоки'


class Discipline(models.Model):
    objects = MyManager()

    code = models.CharField(max_length=5, verbose_name='Код')
    form = models.ForeignKey(DisciplineForm, on_delete=models.SET_NULL, null=True, verbose_name='Форма')

    shifr = models.CharField(max_length=10, default='НЕТ', verbose_name='Шифр')
    name = models.CharField(max_length=128, verbose_name='Дисциплина')

    fakultet = models.ForeignKey(Fakultet, on_delete=models.SET_NULL, null=True, verbose_name='Факультет')

    specialnost = models.ForeignKey(Specialnost, on_delete=models.SET_NULL, null=True, verbose_name='Специальность')

    kurs = models.IntegerField(verbose_name='Курс')

    semestr = models.IntegerField(verbose_name='Семестр')

    PERIOD_CHOICES = [
        ('осенний', 'осенний'),
        ('весенний', 'весенний'),
    ]

    period = models.CharField(max_length=16, choices=PERIOD_CHOICES, default='осенний', verbose_name='Период')

    nedeli = models.IntegerField(verbose_name='Недели')

    trudoemkost = models.IntegerField(verbose_name='Трудоемкость')

    chas_v_nedelu = models.IntegerField(verbose_name='Часы в неделю')

    srs = models.IntegerField(verbose_name='Часов СРС')

    chas_po_planu = models.IntegerField(verbose_name='Часов по плану')

    student = models.IntegerField(verbose_name='Студенты')
    group = models.IntegerField(verbose_name='Группы')
    podgroup = models.IntegerField(verbose_name='Подгруппы')

    lk = models.IntegerField(verbose_name='Лекции')
    pr = models.IntegerField(verbose_name='Практические работы')
    lr = models.IntegerField(verbose_name='Лабараторные работы')

    k_tek = models.DecimalField(max_digits=4, decimal_places=2, verbose_name='Тек.кон.')
    k_ekz = models.DecimalField(max_digits=4, decimal_places=2, verbose_name='Кон.экз')

    zachet = models.DecimalField(max_digits=4, decimal_places=2, verbose_name='Зачет')
    ekzamen = models.DecimalField(max_digits=4, decimal_places=2, verbose_name='Экзамен')

    kontr_raboti = models.DecimalField(max_digits=4, decimal_places=2, verbose_name='Контр. раб.')
    kr_kp = models.IntegerField(verbose_name='КР/КП')
    vkr = models.IntegerField(verbose_name='ВКР')

    pr_ped = models.DecimalField(max_digits=4, decimal_places=2, verbose_name='Практ.пед.')

    pr_dr = models.DecimalField(max_digits=4, decimal_places=2, verbose_name='Практ.другая')

    gak = models.DecimalField(max_digits=4, decimal_places=2, verbose_name='ГАК')

    aspirantura = models.IntegerField(verbose_name='Асп./Магистартура')

    rukovodstvo = models.IntegerField(verbose_name='Руководство')

    dop_chasi = models.IntegerField(verbose_name='Доп. часы')

    kafedra = models.ForeignKey(Kafedra, on_delete=models.SET_NULL, null=True, verbose_name='Кафедра')

    potok = models.ForeignKey(Potok, on_delete=models.SET_NULL, null=True, verbose_name='Поток')

    def summary(self):
        return self.chas_po_planu + self.zachet + self.ekzamen + self.kontr_raboti + self.kr_kp + self.vkr + self.pr_ped + self.pr_dr + self.gak + self.aspirantura + self.rukovodstvo + self.dop_chasi
