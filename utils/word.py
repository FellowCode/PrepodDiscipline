import os

from Prepods.models import Prepod
from utils.shortcuts import get_group_nagruzki, annotate_pochasovka, annotate_group_nagruzki
from docx import Document
from shutil import copyfile


def word_shtat_rasp(request):
    nagruzki_budget = get_group_nagruzki(request, vne_budget=False)
    nagruzki_budget = annotate_pochasovka(nagruzki_budget)
    nagruzki_vnebudget = get_group_nagruzki(request, vne_budget=True)
    nagruzki_vnebudget = annotate_pochasovka(nagruzki_vnebudget)
    nagruzki = annotate_group_nagruzki(nagruzki_budget, nagruzki_vnebudget)

    doc = Document('static/files/Shtat_raspisanie.docx')
    print(doc.tables)
    i = 0
    n_stavka_sum = 0
    n_p_stavka_sum = 0
    n_p_ch_stavka_sum = 0
    v_n_stavka_sum = 0
    v_n_p_stavka_sum = 0
    v_n_p_ch_stavka_sum = 0
    for id, prepod in nagruzki.items():
        n_stavka_sum += prepod['n_stavka']
        n_p_stavka_sum += prepod['pochas_stavka']
        n_p_ch_stavka_sum += prepod['sum_p']
        v_n_stavka_sum += prepod['vnebudget_stavka']
        v_n_p_stavka_sum += prepod['vnebudget_p_stavka']
        v_n_p_ch_stavka_sum += prepod['sum_p_vnebudget']

        row = i + 14
        doc.tables[0].cell(row, 0).text = str(i + 1)
        doc.tables[0].cell(row, 1).text = prepod['prepod__dolzhnost']
        doc.tables[0].cell(row, 2).text = Prepod.get_display_value('PKGD', prepod['prepod__pkgd'])
        doc.tables[0].cell(row, 3).text = str(prepod['prepod__kv_uroven'])
        if prepod['prepod__srok_izbr']:
            doc.tables[0].cell(row, 4).text = prepod['prepod__srok_izbr'].strftime('%d.%m.%Y')
        doc.tables[0].cell(row, 5).text = prepod['prepod__fio']
        st_zv = []
        if prepod['prepod__uch_stepen']:
            st_zv.append(prepod['prepod__uch_stepen'])
        if prepod['prepod__uch_zvanie']:
            st_zv.append(Prepod.get_display_value('UCH_ZVANIE', prepod['prepod__uch_zvanie']))
        doc.tables[0].cell(row, 6).text = ', '.join(st_zv)
        if prepod['prepod__dogovor']:
            doc.tables[0].cell(row, 7).text = 'Договор'
        if prepod['n_stavka'] and prepod['n_stavka'] > 0:
            doc.tables[0].cell(row, 8).text = str(prepod['n_stavka'])
        if prepod['pochas_stavka'] and prepod['pochas_stavka'] > 0:
            doc.tables[0].cell(row, 9).text = f"{prepod['pochas_stavka']}\n({prepod['sum_p']})"
        if prepod['vnebudget_stavka'] and prepod['vnebudget_stavka'] > 0:
            doc.tables[0].cell(row, 10).text = str(prepod['vnebudget_stavka'])
        if prepod['vnebudget_p_stavka'] and prepod['vnebudget_p_stavka'] > 0:
            doc.tables[0].cell(row, 11).text = f"{prepod['vnebudget_p_stavka']}\n({prepod['sum_p_vnebudget']})"
        i += 1

    doc.tables[0].cell(34, 8).text = str(n_stavka_sum)
    doc.tables[0].cell(34, 9).text = f"{n_p_stavka_sum}\n({n_p_ch_stavka_sum})"
    doc.tables[0].cell(34, 10).text = str(v_n_stavka_sum)
    doc.tables[0].cell(34, 11).text = f"{v_n_p_stavka_sum}\n({v_n_p_ch_stavka_sum})"
    doc.tables[0].cell(35, 8).text = str(n_stavka_sum + n_p_stavka_sum)
    doc.tables[0].cell(35, 10).text = str(v_n_stavka_sum + v_n_p_stavka_sum)
    doc.tables[0].cell(36, 8).text = str(n_stavka_sum + n_p_stavka_sum + v_n_stavka_sum + v_n_p_stavka_sum)


    for j in range(32-i-14):
        row = doc.tables[0].rows[i+14]
        remove_row(doc.tables[0], row)



    if not os.path.exists(f'tmp/word/{request.user.id}'):
        os.makedirs(f'tmp/word/{request.user.id}')

    if request.user.prepod.count() > 0:
        kafedra = request.user.prepod.first().kafedra.name
    else:
        kafedra = 'Admin'

    filename = f'{kafedra} - штатное расписание.docx'
    path = f'tmp/word/{request.user.id}/{filename}'

    doc.save(path)

    return path


def remove_row(table, row):
    tbl = table._tbl
    tr = row._tr
    tbl.remove(tr)