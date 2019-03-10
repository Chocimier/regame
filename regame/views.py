from django.shortcuts import render

def challenge():
    return render(request, 'regame/challenge.html')

def match():
    pass

def main(request):
    return render(request, 'regame/main.html')
