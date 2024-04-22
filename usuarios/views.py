from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.messages import constants
from django.contrib.messages import add_message
from django.contrib import auth

# Create your views here.

# Cadastro

def cadastro(request):
    if request.method == "GET":
        return render(request, "cadastro.html")    
    if  request.POST.get('senha') != request.POST.get('confirmar_senha'):
        add_message(request, constants.ERROR, "A senha e a sua confirmação devem ser iguais.")
        return redirect('/usuarios/cadastro')
    if len(request.POST.get('senha')) < 8:
        add_message(request, constants.ERROR, "A senha deve ser maior que 8 (oito) caracteres.")

    users = User.objects.filter(username=request.POST.get('username'))

    if users.exists():
        add_message(request, constants.ERROR, "Username (nome de usuário) já cadastrado.")
        return redirect('/usuarios/cadastro')
    
    try:
        user = User.objects.create_user(
            username = request.POST.get('username'),
            email = request.POST.get('email'),
            password = request.POST.get('senha'))
        return redirect("/usuarios/login")
    except:
        return redirect('/usuarios/cadastro')
    
# Login

def login_view(request):
    if request.method == "GET":
        return render(request, 'login.html')
    elif request.method == "POST":
         user = auth.authenticate(request, 
            username = request.POST.get('username'), 
            password = request.POST.get('senha'))
         if user:
             auth.login(request, user)
             return redirect('/pacientes/home')         
         add_message(request, constants.ERROR, "Usuário ou senha não conferem.")
         return redirect("/usuarios/login")

# Logout

def logout(request):
    auth.logout(request)
    return redirect("/usuarios/login")