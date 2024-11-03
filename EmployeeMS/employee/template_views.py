import json
import requests

from django.contrib.auth import logout
from django.shortcuts import render

def login_page(request):
    return render(request, template_name='login.html')

def logout_page(request):
    logout(request)
    return render(request, template_name='logout.html')

def registration(request):
    return render(request, template_name='registration.html')

def employee_page(request):
    return render(request, template_name='listing.html')

def change_password(request):
    return render(request, template_name='password.html')

def edit_profile_page(request):
    return render(request, template_name='editProfile.html')

def profile_page(request):
    return render(request, template_name='profile.html')
