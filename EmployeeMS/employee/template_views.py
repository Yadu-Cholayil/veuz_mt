import json
import requests

from django.shortcuts import render

def login_page(request):
    return render(request, template_name='login.html')

def registration(request):
    return render(request, template_name='registration.html')

def employee_page(request):
    return render(request, template_name='listing.html')

def change_password(request):
    return render(request, template_name='password.html')

def profile_page(request):
    return render(request, template_name='profile.html')