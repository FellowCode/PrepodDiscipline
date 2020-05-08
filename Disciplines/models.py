from django.db import models
from utils.model_manager import MyManager
from Prepods.models import Prepod


class DisciplineForm(models.Model):
    objects = MyManager()

    name = models.CharField(max_length=256, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Форма дисциплины'
        verbose_name_plural = 'Формы дисциплины'


class Fakultet(models.Model):
    objects = MyManager()

    name = models.CharField(max_length=256, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Факультет'
        verbose_name_plural = 'Факультеты'


class Specialnost(models.Model):
    objects = MyManager()

    name = models.CharField(max_length=256, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Специальность'
        verbose_name_plural = 'Специальности'


class Kafedra(models.Model):
    objects = MyManager()

    name = models.CharField(max_length=256, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Кафедра'
        verbose_name_plural = 'Кафедры'


class Potok(models.Model):
    objects = MyManager()

    name = models.CharField(max_length=256, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Поток'
        verbose_name_plural = 'Потоки'


class Discipline(models.Model):
    objects = MyManager()

    code = models.CharField(max_length=16, verbose_name='Код')
    form = models.ForeignKey(DisciplineForm, on_delete=models.SET_NULL, null=True, verbose_name='Форма')

    shifr = models.CharField(max_length=10, default='НЕТ', verbose_name='Шифр')
    name = models.CharField(max_length=1024, verbose_name='Дисциплина')

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
    kr_kp = models.DecimalField(max_digits=4, decimal_places=2, verbose_name='КР/КП')
    vkr = models.DecimalField(max_digits=4, decimal_places=2, verbose_name='ВКР')

    pr_ped = models.DecimalField(max_digits=4, decimal_places=2, verbose_name='Практ.пед.')

    pr_dr = models.DecimalField(max_digits=4, decimal_places=2, verbose_name='Практ.другая')

    gak = models.DecimalField(max_digits=4, decimal_places=2, verbose_name='ГАК')

    aspirantura = models.DecimalField(max_digits=4, decimal_places=2, verbose_name='Асп./Магистартура')

    rukovodstvo = models.DecimalField(max_digits=4, decimal_places=2, verbose_name='Руководство')

    dop_chasi = models.DecimalField(max_digits=4, decimal_places=2, verbose_name='Доп. часы')

    kafedra = models.ForeignKey(Kafedra, on_delete=models.SET_NULL, null=True, verbose_name='Кафедра')

    potok = models.ForeignKey(Potok, on_delete=models.SET_NULL, null=True, verbose_name='Поток')

    def summary(self):
        return self.k_tek + self.k_ekz + self.lk + self.lr + self.pr + self.zachet + self.ekzamen + self.kontr_raboti + self.kr_kp + self.vkr + self.pr_ped + self.pr_dr + self.gak + self.aspirantura + self.rukovodstvo + self.dop_chasi

    def spec_and_form(self):
        return f'{self.specialnost.name} ({self.form.name})'

    def group_podgroup(self):
        return f'{self.group}/{self.podgroup}'

    def audit_chasov(self):
        return self.lk + self.pr + self.lr

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Дисциплина'
        verbose_name_plural = 'Дисциплины'
        ordering = ['name']


class Archive(models.Model):
    discipline = models.ForeignKey(Discipline, on_delete=models.CASCADE)

    dt = models.DateTimeField(auto_now_add=True, verbose_name='Дата')

    class Meta:
        verbose_name = 'Архив'
        verbose_name_plural = 'Архивы'



class Nagruzka(models.Model):
    discipline = models.ForeignKey(Discipline, on_delete=models.SET_NULL, null=True, verbose_name="Дисциплина")

    archive = models.ForeignKey(Archive, on_delete=models.SET_NULL, null=True, default=None, related_name='nagruzki')

    prepod = models.ForeignKey(Prepod, on_delete=models.SET_NULL, null=True, verbose_name="Преподаватель")

    student = models.IntegerField(verbose_name='Студентов')

    lk = models.IntegerField(verbose_name='Лекции', default=0)
    pr = models.IntegerField(verbose_name='Практические работы', default=0)
    lr = models.IntegerField(verbose_name='Лабараторные работы', default=0)

    k_tek = models.DecimalField(max_digits=4, decimal_places=2, verbose_name='Тек.кон.', default=0)
    k_ekz = models.DecimalField(max_digits=4, decimal_places=2, verbose_name='Кон.экз', default=0)

    zachet = models.DecimalField(max_digits=4, decimal_places=2, verbose_name='Зачет', default=0)
    ekzamen = models.DecimalField(max_digits=4, decimal_places=2, verbose_name='Экзамен', default=0)

    kontr_raboti = models.DecimalField(max_digits=4, decimal_places=2, verbose_name='Контр. раб.', default=0)
    kr_kp = models.DecimalField(max_digits=4, decimal_places=2, verbose_name='КР/КП', default=0)
    vkr = models.DecimalField(max_digits=4, decimal_places=2, verbose_name='ВКР', default=0)

    pr_ped = models.DecimalField(max_digits=4, decimal_places=2, verbose_name='Практ.пед.', default=0)

    pr_dr = models.DecimalField(max_digits=4, decimal_places=2, verbose_name='Практ.другая', default=0)

    gak = models.DecimalField(max_digits=4, decimal_places=2, verbose_name='ГАК', default=0)

    aspirantura = models.DecimalField(max_digits=4, decimal_places=2, verbose_name='Асп./Магистартура', default=0)

    rukovodstvo = models.DecimalField(max_digits=4, decimal_places=2, verbose_name='Руководство', default=0)

    dop_chasi = models.DecimalField(max_digits=4, decimal_places=2, verbose_name='Доп. часы', default=0)

    class Meta:
        verbose_name = 'Нагрузка'
        verbose_name_plural = 'Нагрузки'

    def summary(self):
        return self.k_tek + self.k_ekz + self.lk + self.lr + self.pr + self.zachet + self.ekzamen + self.kontr_raboti + self.kr_kp + self.vkr + self.pr_ped + self.pr_dr + self.gak + self.aspirantura + self.rukovodstvo + self.dop_chasi


