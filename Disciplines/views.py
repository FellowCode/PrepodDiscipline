from django.http import HttpResponse, JsonResponse, Http404
from django.shortcuts import render, reverse
from .models import Discipline

from utils.xls import handle_upload_disciplines, create_disciplines_xls

def disciplines_list(request):
    disciplines = Discipline.objects.all()
    return render(request, 'Disciplines/List.html', {'disciplines': disciplines})

def disciplines_upload(request):
    if request.user.is_superuser and request.is_ajax() and request.method == 'POST':
        handle_upload_disciplines(request.FILES['disciplines'], request.POST.get('action'))
        return JsonResponse({'status': 'OK'})
    raise Http404

def disciplines_download(request):
    if request.is_ajax() and request.method == 'POST':
        create_disciplines_xls()
        return JsonResponse({'status': 'OK'})
    raise Http404
