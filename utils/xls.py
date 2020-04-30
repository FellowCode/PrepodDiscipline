def handle_upload_disciplines(f):
    with open('tmp/xls/disciplines.xls', 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    print('upload complete!')
