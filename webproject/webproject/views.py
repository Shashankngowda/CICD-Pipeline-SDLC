from django.shortcuts import render,redirect
from django.core.validators import EmailValidator



def homepage(request):
    return render(request,"index.html")

def user_de(request):

    return render(request,'user_details.html')


def sum(request):
    return render(request,"summary.html")

