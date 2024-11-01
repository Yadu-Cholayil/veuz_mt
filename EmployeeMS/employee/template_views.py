import requests

from django.shortcuts import render

def token_auth():
    token_url = 'http://127.0.0.1:8000/api/token/'
    credentials = {
        'username': 'YKC',
        'password': '12345678'
    }
    response = requests.post(token_url, json=credentials)
    if response.status_code == 200:
        tokens = response.json()
        access_token = tokens['access']
        position = tokens['position']

        # Step 2: Use the JWT token in a subsequent request
        headers = {
            'Authorization': f'Bearer {access_token}',
            'postion': position
        }

        return headers

def login_page(request):
    return render(request, template_name='login.html')

def registration(request):
    return render(request, template_name='registration.html')

def employee_page(request):
    data = requests.get('http://127.0.0.1:8000/employees/employee/', headers=token_auth()).json()
    print({'employees':data})
    return render(request, template_name='listing.html', context={'employees':data})