from django.shortcuts import render

def home(request):
    return render(request, 'frontend/home.html')

def tourist_register(request):
    return render(request, 'frontend/tourist_register.html')

def local_register(request):
    return render(request, 'frontend/local_register.html')

def login_page(request):
    return render(request, 'frontend/login.html')

def dashboard(request):
    auth_token = None
    if request.user.is_authenticated:
        from rest_framework.authtoken.models import Token
        token_obj, _ = Token.objects.get_or_create(user=request.user)
        auth_token = token_obj.key
    return render(request, 'frontend/dashboard.html', {
        'auth_token': auth_token,
        'user_name': request.user.first_name or request.user.username if request.user.is_authenticated else 'Guest'
    })

def plan_trip(request):
    return render(request, 'frontend/plan.html')
