from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.

def edit_code_index(request):
    return render(request,'edit_code.html')


def save_code(request):
    print(request.POST.get('code'))
    return HttpResponse('123')
