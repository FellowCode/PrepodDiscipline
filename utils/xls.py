import os
from django.conf import settings
import xlrd, xlwt
from xlutils.copy import copy

from Disciplines.models import *
from utils.decorators import make_async
from queue import LifoQueue
from time import sleep
from .shortcuts import get_group_nagruzki, annotate_pochasovka, annotate_group_nagruzki

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


def excel_shtat_rasp(request):
    nagruzki_budget = get_group_nagruzki(request, vne_budget=False)
    nagruzki_budget = annotate_pochasovka(nagruzki_budget)
    nagruzki_vnebudget = get_group_nagruzki(request, vne_budget=True)
    nagruzki_vnebudget = annotate_pochasovka(nagruzki_vnebudget)
    nagruzki = annotate_group_nagruzki(nagruzki_budget, nagruzki_vnebudget)

    rb = xlrd.open_workbook('static/files/st_r.xls', formatting_info=True)
    wb = copy(rb)
    sheet = wb.get_sheet(0)
    i = 0
    n_stavka_sum = 0
    n_p_stavka_sum = 0
    n_p_ch_stavka_sum = 0
    v_n_stavka_sum = 0
    v_n_p_stavka_sum = 0
    v_n_p_ch_stavka_sum = 0
    for id, prepod in nagruzki.items():
        row = i + 12
        n_stavka_sum += prepod.get('n_stavka', 0)
        n_p_stavka_sum += prepod.get('pochas_stavka', 0)
        n_p_ch_stavka_sum += prepod.get('sum_p', 0)
        v_n_stavka_sum += prepod.get('vnebudget_stavka', 0)
        v_n_p_stavka_sum += prepod.get('vnebudget_p_stavka', 0)
        v_n_p_ch_stavka_sum += prepod.get('sum_p_vnebudget', 0)

        setOutCell(sheet, row, 0, i + 1)
        setOutCell(sheet, row, 1, prepod['prepod__dolzhnost'])
        setOutCell(sheet, row, 2, Prepod.get_display_value('PKGD', prepod['prepod__pkgd']))
        setOutCell(sheet, row, 3, prepod['prepod__kv_uroven'])
        if prepod['prepod__srok_izbr']:
            setOutCell(sheet, row, 4, prepod['prepod__srok_izbr'].strftime('%d.%m.%Y'))
        setOutCell(sheet, row, 5, prepod['prepod__fio'])
        st_zv = []
        if prepod['prepod__uch_stepen']:
            st_zv.append(prepod['prepod__uch_stepen'])
        if prepod['prepod__uch_zvanie']:
            st_zv.append(Prepod.get_display_value('UCH_ZVANIE', prepod['prepod__uch_zvanie']))
        setOutCell(sheet, row, 6, ', '.join(st_zv))
        if prepod['prepod__dogovor']:
            setOutCell(sheet, row, 7, 'Договор')
        if prepod.get('n_stavka') and prepod['n_stavka'] > 0:
            setOutCell(sheet, row, 8, prepod['n_stavka'])
        if prepod.get('pochas_stavka') and prepod['pochas_stavka'] > 0:
            setOutCell(sheet, row, 9, f"{prepod['pochas_stavka']}\n({prepod['sum_p']})")
        if prepod.get('vnebudget_stavka') and prepod['vnebudget_stavka'] > 0:
            setOutCell(sheet, row, 10, prepod['vnebudget_stavka'])
        if prepod.get('vnebudget_p_stavka') and prepod['vnebudget_p_stavka'] > 0:
            setOutCell(sheet, row, 11, f"{prepod['vnebudget_p_stavka']}\n({prepod['sum_p_vnebudget']})")
        i += 1

    setOutCell(sheet, 99, 8, n_stavka_sum)
    setOutCell(sheet, 99, 9, f"{n_p_stavka_sum}\n({n_p_ch_stavka_sum})")
    setOutCell(sheet, 99, 10, v_n_stavka_sum)
    setOutCell(sheet, 99, 11, f"{v_n_p_stavka_sum}\n({v_n_p_ch_stavka_sum})")
    setOutCell(sheet, 100, 8, n_stavka_sum + n_p_stavka_sum)
    setOutCell(sheet, 100, 10, v_n_stavka_sum + v_n_p_stavka_sum)
    setOutCell(sheet, 101, 8, n_stavka_sum + n_p_stavka_sum + v_n_stavka_sum + v_n_p_stavka_sum)

    if not os.path.exists(f'tmp/xls/{request.user.id}'):
        os.makedirs(f'tmp/xls/{request.user.id}')
    if request.user.prepod.count() > 0:
        kafedra = request.user.prepod.first().kafedra.name
    else:
        kafedra = 'Admin'
    filename = f'{kafedra} - штатное расписание.xls'
    path = f'tmp/xls/{request.user.id}/{filename}'
    wb.save(path)

    return path
