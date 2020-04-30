import os
from django.conf import settings
import xlrd, xlwt

def handle_upload_disciplines(f):
    if not os.path.exists('tmp/xls'):
        os.makedirs('tmp/xls')
    ext = f.name.split('.')[-1]
    with open('tmp/xls/disciplines.'+ext, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    print('upload complete!')
