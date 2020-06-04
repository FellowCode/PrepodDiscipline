import os
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
    print(delete_disciplines_id)
    global upload_progress
    for rownum in range(1, sheet.nrows):
        if sheet.row_values(rownum)[0] == '':
            break
        d = Discipline.objects.get_or_new(code=int(sheet.row_values(rownum)[0]))
        for i, val in enumerate(sheet.row_values(rownum)):
            if i < len(CELL_NAMES):
                if CELL_NAMES[i] in FK:
                    related = FK[CELL_NAMES[i]].objects.get_or_new(name=val)
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


def create_prep_ds_xls(prepod):
    CELL_NAMES = ['name', 'spec_and_form', 'kurs', 'group_podgroup', 'student', 'trudoemkost',
                  'audit_chasov', 'srs', 'lk', 'pr', 'lr', 'k_tek', 'k_ekz', 'zachet',
                  'ekzamen', 'kontr_raboti', 'kr_kp', 'vkr', 'pr_ped', 'pr_dr', 'gak',
                  'aspirantura', 'rukovodstvo', 'dop_chasi', 'summary']

    rb = xlrd.open_workbook('static/files/prep_ds_shablon.xls', formatting_info=True)
    wb = copy(rb)
    sheet = wb.get_sheet(0)
    setOutCell(sheet, 6, 1, f'{prepod.last_name} {prepod.first_name} {prepod.surname}')
    setOutCell(sheet, 6, 13, f'{prepod.dolzhnost.name}, {prepod.kv_uroven}')
    setOutCell(sheet, 7, 14, prepod.n_stavka)

    ds = prepod.disciplines.all()
    osen = 0
    vesna = 0

    for d in ds:
        print(d.period)
        for j, key in enumerate(CELL_NAMES):
            val = getattr(d, key)
            if callable(val):
                val = val()
            if key in FK:
                val = val.name
            if d.period == 'осенний':
                setOutCell(sheet, osen + 10, j + 1, val)
            else:
                setOutCell(sheet, vesna + 72, j + 1, val)

        if d.period == 'осенний':
            setOutCell(sheet, osen + 10, 0, osen + 1)
            osen += 1
        else:
            setOutCell(sheet, vesna + 72, 0, vesna + 1)
            vesna += 1

    filename = f'{prepod.fio()} - дисциплины.xls'
    url = f'static/files/{filename}'
    wb.save(url)
    return '/' + url, filename


def excel_shtat_rasp(request, fakultet_id=None, _all=False):
    if fakultet_id == '':
        fakultet_id = None
    fakultet = Fakultet.objects.get_or_none(id=fakultet_id)
    prepods = get_shtat_rasp(request, fakultet, _all)
    rb = xlrd.open_workbook('static/files/st_r.xls', formatting_info=True)
    wb = copy(rb)
    sheet = wb.get_sheet(0)

    for i, row in enumerate(prepods['rows']):
        setOutCell(sheet, row + 14, 0, i + 1)
        for j, col in enumerate(row):
            setOutCell(sheet, row + 14, j + 1, col)

    setOutCell(sheet, 99, 8, prepods['sums']['n_stavka_sum'])
    setOutCell(sheet, 99, 9, f"{prepods['sums']['n_p_stavka_sum']}\n({prepods['sums']['n_p_ch_stavka_sum']})")
    setOutCell(sheet, 99, 10, prepods['sums']['v_n_stavka_sum'])
    setOutCell(sheet, 99, 11, f"{prepods['sums']['v_n_p_stavka_sum']}\n({prepods['sums']['v_n_p_ch_stavka_sum']})")
    setOutCell(sheet, 100, 8, prepods['sums']['n_stavka_sum'] + prepods['sums']['n_p_stavka_sum'])
    setOutCell(sheet, 100, 10, prepods['sums']['v_n_stavka_sum'] + prepods['sums']['v_n_p_stavka_sum'])
    setOutCell(sheet, 101, 8, prepods['sums']['n_stavka_sum'] + prepods['sums']['n_p_stavka_sum'] + prepods['sums']['v_n_stavka_sum'] + prepods['sums']['v_n_p_stavka_sum'])

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
