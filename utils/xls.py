import os
from django.conf import settings
import xlrd, xlwt
from xlutils.copy import copy

from Disciplines.models import *

cell_names = ['code', 'form', 'shifr', 'name', 'fakultet', 'specialnost', 'kurs', 'semestr', 'period', 'nedeli',
              'trudoemkost', 'chas_v_nedelu', 'srs', 'chas_po_planu', 'student', 'group', 'podgroup', 'lk', 'pr',
              'lr', 'k_tek', 'k_ekz', 'zachet', 'ekzamen', 'kontr_raboti', 'kr_kp', 'vkr', 'pr_ped', 'pr_dr', 'gak',
              'aspirantura', 'rukovodstvo', 'dop_chasi', 'summary', 'kafedra', 'potok']
fk = {'form': DisciplineForm, 'fakultet': Fakultet, 'specialnost': Specialnost, 'kafedra': Kafedra, 'potok': Potok}

def handle_upload_disciplines(f, action):
    if not os.path.exists('tmp/xls'):
        os.makedirs('tmp/xls')
    ext = f.name.split('.')[-1]
    filename = 'tmp/xls/upload.' + ext
    with open(filename, 'wb') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

    rb = xlrd.open_workbook(filename)
    if action == 'replace':
        Discipline.objects.all().delete()
        sheet = rb.sheet_by_index(0)
        for rownum in range(1, sheet.nrows-1):
            d = Discipline()
            for i, val in enumerate(sheet.row_values(rownum)):
                if i < len(cell_names):
                    if cell_names[i] == 'summary':
                        continue
                    if cell_names[i] in fk:
                        related = fk[cell_names[i]].objects.get_or_new(name=val)
                        related.save()
                        setattr(d, cell_names[i], related)
                    else:
                        d.__dict__[cell_names[i]] = val
            d.save()


def create_disciplines_xls():
    rb = xlrd.open_workbook('static/files/Shablon.xls')
    wb = copy(rb)
    sheet = wb.get_sheet(0)
    ds = Discipline.objects.all()
    for i, d in enumerate(ds):
        for j, key in enumerate(cell_names):
            val = getattr(d, key)
            if key == 'summary':
                val = val()
            if key in fk:
                val = val.name
            sheet.write(i+1, j, val)
    wb.save('static/files/disciplines.xls')
