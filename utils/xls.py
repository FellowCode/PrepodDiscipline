import os
from datetime import datetime

from django.conf import settings
import xlrd, xlwt
from xlutils.copy import copy

from Disciplines.models import *
from utils.decorators import make_async
from queue import LifoQueue
from time import sleep
from .shortcuts import get_group_nagruzki, annotate_pochasovka, annotate_group_nagruzki, get_shtat_rasp

CELL_NAMES = ['code', 'form', 'shifr', 'name', 'fakultet', 'specialnost', 'kurs', 'semestr', 'period', 'nedeli',
              'trudoemkost', 'chas_v_nedelu', 'srs', 'chas_po_planu', 'student', 'group', 'podgroup', 'lk', 'pr',
              'lr', 'k_tek', 'k_ekz', 'zachet', 'ekzamen', 'kontr_raboti', 'kr_kp', 'vkr', 'pr_ped', 'pr_dr', 'gak',
              'aspirantura', 'rukovodstvo', 'dop_chasi', 'summary', 'kafedra', 'potok']

FK = {'form': DisciplineForm, 'fakultet': Fakultet, 'specialnost': Specialnost, 'kafedra': Kafedra, 'potok': Potok}


def _getOutCell(outSheet, colIndex, rowIndex):
    """ HACK: Extract the internal xlwt cell representation. """
    row = outSheet._Worksheet__rows.get(rowIndex)
    if not row: return None

    cell = row._Row__cells.get(colIndex)
    return cell


def setOutCell(outSheet, row, col, value):
    """ Change cell value without changing formatting. """
    # HACK to retain cell style.
    previousCell = _getOutCell(outSheet, col, row)
    # END HACK, PART I

    outSheet.write(row, col, value)

    # HACK, PART II
    if previousCell:
        newCell = _getOutCell(outSheet, col, row)
        if newCell:
            newCell.xf_idx = previousCell.xf_idx

    # END HACK


def handle_upload_disciplines(f, action):
    if not os.path.exists('tmp/xls'):
        os.makedirs('tmp/xls')
    ext = f.name.split('.')[-1]
    filename = 'tmp/xls/upload.' + ext
    with open(filename, 'wb') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

    global upload_progress

    global parsing
    parsing = True
    upload_progress = '0/0 0 %'

    parse_xls_disciplines(filename)


upload_progress = '0/0 0 %'
parsing = False


@make_async
def parse_xls_disciplines(filename):
    rb = xlrd.open_workbook(filename, encoding_override="cp1251")
    sheet = rb.sheet_by_index(0)
    new_disciplines_id = []
    delete_disciplines_id = list(Discipline.objects.all().values_list('id', flat=True))
    delete_objects = {'form': list(DisciplineForm.objects.all().values_list('id', flat=True)),
                      'fakultet': list(Fakultet.objects.all().values_list('id', flat=True)),
                      'kafedra': list(Kafedra.objects.all().values_list('id', flat=True)),
                      'potok': list(Potok.objects.all().values_list('id', flat=True)),
                      'specialnost': list(Specialnost.objects.all().values_list('id', flat=True))}
    global upload_progress
    for rownum in range(1, sheet.nrows):
        if sheet.row_values(rownum)[0] == '':
            break
        d = Discipline.objects.get_or_new(code=int(sheet.row_values(rownum)[0]))
        for i, val in enumerate(sheet.row_values(rownum)):
            if type(val) == str:
                val = val.strip()
            if i < len(CELL_NAMES):
                if CELL_NAMES[i] in FK:
                    related = FK[CELL_NAMES[i]].objects.get_or_new(name=val)
                    if related.id in delete_objects[CELL_NAMES[i]]:
                        delete_objects[CELL_NAMES[i]].remove(related.id)
                    if CELL_NAMES[i] == 'kafedra' and d.fakultet.name != 'НЕТ':
                        related.fakultet = d.fakultet
                    related.save()
                    setattr(d, CELL_NAMES[i], related)
                else:
                    try:
                        val = float(val)
                    except:
                        pass
                    d.__dict__[CELL_NAMES[i]] = val
        d.check_nagruzka_sum()
        d.save()
        new_disciplines_id.append(d.id)
        if d.id in delete_disciplines_id:
            delete_disciplines_id.remove(d.id)
        if rownum % 30 == 0:
            upload_progress = f'{rownum}/{sheet.nrows} {int(rownum / sheet.nrows * 100)} %'

    for key, id_list in delete_objects.items():
        FK[key].objects.filter(id__in=id_list).delete()

    while len(delete_disciplines_id) > 500:
        Discipline.objects.filter(id__in=delete_disciplines_id[:500]).delete()
        delete_disciplines_id = delete_disciplines_id[500:]
    Discipline.objects.filter(id__in=delete_disciplines_id).delete()

    global parsing
    parsing = False
    upload_progress = '0/0 0 %'


def create_disciplines_xls():
    rb = xlrd.open_workbook('static/files/Shablon.xls')
    wb = copy(rb)
    sheet = wb.get_sheet(0)
    ds = Discipline.objects.all()
    for i, d in enumerate(ds):
        for j, key in enumerate(CELL_NAMES):
            val = getattr(d, key)
            if key == 'summary':
                val = val()
            if key in FK:
                val = val.name
            sheet.write(i + 1, j, val)
    wb.save('static/files/disciplines.xls')


def create_prep_cart_xls(user, prepod, _type, stavka):
    if type(stavka) == str:
        stavka = stavka.split('\n')[0]
    CELL_NAMES = ['dis:name', 'dis:spec_and_form', 'dis:kurs', 'dis:group_podgroup', 'student', 'dis:trudoemkost',
                  'dis:audit_chasov', 'dis:srs', 'lk', 'pr', 'lr', 'k_tek', 'k_ekz', 'zachet',
                  'ekzamen', 'kontr_raboti', 'kr_kp', 'vkr', 'pr_ped', 'pr_dr', 'gak',
                  'aspirantura', 'rukovodstvo', 'dop_chasi', 'summary']
    SUM_CELLS = ['dis:trudoemkost', 'dis:audit_chasov', 'dis:srs', 'lk', 'pr', 'lr', 'k_tek', 'k_ekz', 'zachet',
                 'ekzamen', 'kontr_raboti', 'kr_kp', 'vkr', 'pr_ped', 'pr_dr', 'gak',
                 'aspirantura', 'rukovodstvo', 'dop_chasi', 'summary']

    ds = prepod.nagruzki.filter(archive=None)
    if ds.count() == 0:
        return None

    rb = xlrd.open_workbook('static/files/prep_ds_shablon.xls', formatting_info=True)
    wb = copy(rb)
    sheet = wb.get_sheet(0)
    setOutCell(sheet, 6, 1, f'{prepod.last_name} {prepod.first_name} {prepod.surname}')
    setOutCell(sheet, 6, 13, f'{prepod.dolzhnost}, {prepod.kv_uroven}')
    setOutCell(sheet, 7, 14, stavka)
    setOutCell(sheet, 7, 18, 'бюджет')

    if _type == 'b':
        ds = ds.exclude(Q(discipline__form__name__contains='_В') | Q(pochasovka=True))
        setOutCell(sheet, 7, 18, 'бюджет')
    elif _type == 'b_p':
        ds = ds.exclude(Q(discipline__form__name__contains='_В') | Q(pochasovka=False))
        setOutCell(sheet, 7, 18, 'бюджет')
    elif _type == 'vb':
        ds = ds.filter(discipline__form__name__contains='_В', pochasovka=False)
        setOutCell(sheet, 7, 18, 'внебюджет')
    elif _type == 'vb_p':
        ds = ds.filter(discipline__form__name__contains='_В', pochasovka=True)
        setOutCell(sheet, 7, 18, 'внебюджет')

    osen = 0
    vesna = 0
    year = 0

    sums_osen = [0] * len(SUM_CELLS)
    sums_vesna = [0] * len(SUM_CELLS)
    sums_year = [0] * len(SUM_CELLS)

    for d in ds:
        for j, key in enumerate(CELL_NAMES):
            if 'dis:' in key:
                val = getattr(d.discipline, key.split(':')[1])
            else:
                val = getattr(d, key)
            if callable(val):
                val = val()
            if key in FK:
                val = val.name
            if key in SUM_CELLS:
                sum_i = SUM_CELLS.index(key)
            else:
                sum_i = None
            if d.discipline.period == 'осенний':
                setOutCell(sheet, osen + 10, j + 1, val)
                if sum_i:
                    sums_osen[sum_i] += float(val)
            elif d.discipline.period == 'весенний':
                setOutCell(sheet, vesna + 72, j + 1, val)
                if sum_i:
                    sums_vesna[sum_i] += float(val)
            else:
                setOutCell(sheet, year + 132, j + 1, val)
                if sum_i:
                    sums_year[sum_i] += float(val)

        if d.discipline.period == 'осенний':
            setOutCell(sheet, osen + 10, 0, osen + 1)
            osen += 1
        elif d.discipline.period == 'весенний':
            setOutCell(sheet, vesna + 72, 0, vesna + 1)
            vesna += 1
        else:
            setOutCell(sheet, year + 132, 0, year + 1)
            year += 1

    for n, sum in enumerate(sums_osen):
        setOutCell(sheet, 60, n + 6, sum)
    for n, sum in enumerate(sums_vesna):
        setOutCell(sheet, 122, n + 6, sum)
    for n, sum in enumerate(sums_year):
        setOutCell(sheet, 182, n + 6, sum)

    # sheet.getCells().deleteRows(9+osen, 50-osen, True)

    if not os.path.exists(f'tmp/xls/{user.id}'):
        os.makedirs(f'tmp/xls/{user.id}')

    if _type == 'b':
        filename = f"Карточка {prepod.fio} ст_{str(stavka)}_{datetime.now().strftime('%d.%m.%Y')}б.xls"
    elif _type == 'b_p':
        filename = f"Карточка {prepod.fio} ст_{str(stavka)}_П_{datetime.now().strftime('%d.%m.%Y')}б.xls"
    elif _type == 'vb':
        filename = f"Карточка {prepod.fio} ст_{str(stavka)}_{datetime.now().strftime('%d.%m.%Y')}в.xls"
    elif _type == 'vb_p':
        filename = f"Карточка {prepod.fio} ст_{str(stavka)}_П_{datetime.now().strftime('%d.%m.%Y')}в.xls"
    else:
        filename = f"Карточка {prepod.fio} ст_{str(stavka)}_{datetime.now().strftime('%d.%m.%Y')}.xls"

    path = f'tmp/xls/{user.id}/{filename}'
    wb.save(path)
    # remove_rows(path, 9 + osen, 50 - osen)
    return path


def excel_shtat_rasp(request, fakultet_id=None, _all=False):
    if fakultet_id == '':
        fakultet_id = None
    fakultet = Fakultet.objects.get_or_none(id=fakultet_id)
    prepods = get_shtat_rasp(request, fakultet, _all)
    rb = xlrd.open_workbook('static/files/st_r.xls', formatting_info=True)
    wb = copy(rb)
    sheet = wb.get_sheet(0)
    i = 0
    for id, row in prepods['rows'].items():
        setOutCell(sheet, i + 12, 0, i + 1)
        for j, col in enumerate(row):
            setOutCell(sheet, i + 12, j + 1, col)
        i += 1

    setOutCell(sheet, 99, 8, prepods['sums']['n_stavka_sum'])
    setOutCell(sheet, 99, 9, f"{prepods['sums']['n_p_stavka_sum']}\n({prepods['sums']['n_p_ch_stavka_sum']})")
    setOutCell(sheet, 99, 10, prepods['sums']['v_n_stavka_sum'])
    setOutCell(sheet, 99, 11, f"{prepods['sums']['v_n_p_stavka_sum']}\n({prepods['sums']['v_n_p_ch_stavka_sum']})")
    setOutCell(sheet, 100, 8, prepods['sums']['n_stavka_sum'] + prepods['sums']['n_p_stavka_sum'])
    setOutCell(sheet, 100, 10, prepods['sums']['v_n_stavka_sum'] + prepods['sums']['v_n_p_stavka_sum'])
    setOutCell(sheet, 101, 8,
               prepods['sums']['n_stavka_sum'] + prepods['sums']['n_p_stavka_sum'] + prepods['sums']['v_n_stavka_sum'] +
               prepods['sums']['v_n_p_stavka_sum'])

    if not os.path.exists(f'tmp/xls/{request.user.id}'):
        os.makedirs(f'tmp/xls/{request.user.id}')

    if not request.user.is_superuser and not _all:
        kafedra = request.user.prepod.first().kafedra.name
    else:
        kafedra = 'Все кафедры'

    if fakultet:
        filename = f'{fakultet.name} - штатное расписание.xls'
    else:
        filename = f'{kafedra} - штатное расписание.xls'
    path = f'tmp/xls/{request.user.id}/{filename}'
    wb.save(path)

    return path


def otvet_fakultetu(request):
    if request.user.is_superuser:
        return None

    CELL_NAMES = ['dis:semestr', 'dis:period', 'dis:nedeli', 'dis:trudoemkost', 'dis:chas_v_nedelu', 'dis:srs',
                  'dis:chas_po_planu', 'student', 'dis:group', 'dis:podgroup', 'lk', 'pr', 'lr', 'k_ekz',
                  'zachet', 'ekzamen', 'kontr_raboti', 'kr_kp', 'vkr',
                  'pr_ped', 'pr_dr', 'gak', 'aspirantura', 'rukovodstvo', 'dop_chasi', 'summary', 'prepod']

    rb = xlrd.open_workbook('static/files/otvet_fakultetu.xls', formatting_info=True)
    wb = copy(rb)
    sheet = wb.get_sheet(0)

    kafedra = request.user.prepod.first().kafedra
    nagruzki = Nagruzka.objects.select_related('discipline').filter(archive=None, discipline__kafedra=kafedra)

    style = xlwt.XFStyle()
    borders = xlwt.Borders()
    borders.bottom = xlwt.Borders.THIN
    borders.top = xlwt.Borders.THIN
    borders.left = xlwt.Borders.THIN
    borders.right = xlwt.Borders.THIN
    style.borders = borders

    for i, nagruzka in enumerate(nagruzki):
        for j, cell in enumerate(CELL_NAMES):
            if 'dis:' in cell:
                val = getattr(nagruzka.discipline, cell.split(':')[1])
            else:
                val = getattr(nagruzka, cell)
            if callable(val):
                val = val()
            if cell == 'prepod':
                val = val.fio
            sheet.write(i+1, j, val, style=style)

    if not os.path.exists(f'tmp/xls/{request.user.id}'):
        os.makedirs(f'tmp/xls/{request.user.id}')

    filename = f"Ответ {kafedra} факультету {kafedra.fakultet} {datetime.now().strftime('%d.%m.%Y')}.xls"
    path = f'tmp/xls/{request.user.id}/{filename}'
    wb.save(path)
    return path
