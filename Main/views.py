from django.shortcuts import render
import pprint


pp = pprint.PrettyPrinter()




def index(request):
    return render(request, 'Main/Index.html')
