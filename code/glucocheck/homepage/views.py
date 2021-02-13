from django.shortcuts import render, redirect
from django.http import HttpResponse
from homepage.forms import SignupForm
from django.contrib import messages

# Create your views here.

def home(request):
    
    return render(request,'homepage/home.html')

def signup(request):

    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            user.first_name = cleaned_data['first_name']
            user.last_name = cleaned_data['last_name']
            user.email = cleaned_data['email']
            user.country = cleaned_data['country']
            messages.success(request,'Account created successfully')
            return redirect('login')
    else: 
        form = SignupForm()

    return render(request,'homepage/signup.html', {'form': form})


def login(request):
    
    return render(request,'homepage/login.html')