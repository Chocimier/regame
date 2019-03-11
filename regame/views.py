from django.http import HttpResponse
from django.shortcuts import render

def challenge():
    return render(request, 'regame/challenge.html')

def match(request, no):
    return HttpResponse(str(no))

def main(request):
    return render(request, 'regame/main.html')
