from django.shortcuts import render, redirect
from django.http import HttpResponse
from homepage.forms import SignupForm
from django.contrib import messages
from django.contrib.auth import login, authenticate,logout

# Create your views here.

def homepage(request):
    ''' Snippet of the code for inputting the user name into the template
    if request.user.is_authenticated:
        context = {'username': f'Welcome {request.user.name}!', 'active': 'Home'} # or however you reference the user name
    else:
        context = {'username': 'Sign-In/Up', 'active': 'Home'}
        
    The 'activate' context item represents which navbar is selected and therefore should be coloured differently
    '''
    context = {'username': 'Sign-In/Up',
               'active': 'Home'}
    return render(request, 'homepage/homepage.html', context)


def signup(request):

    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            user = form.cleaned_data.get('username')
                       
            messages.success(request,'Account created successfully for' + user)
            return redirect('login')
    else: 
        form = SignupForm()

    return render(request,'account/signup.html', {'form': form})


def login(request):
    
    return render(request,'account/login.html')
