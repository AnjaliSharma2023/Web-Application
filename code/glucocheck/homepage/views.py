from django.shortcuts import render, redirect
from django.http import HttpResponse
from homepage.forms import SignupForm
from django.contrib import messages

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
            username = form.cleaned_data.get('username')
            #user.last_name = form.cleaned_data['last_name']
            #user.email = form.cleaned_data['email']
            #user.country = form.cleaned_data['country']

            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            
            messages.success(request,'Account created successfully')
            return redirect('login')
    else: 
        form = SignupForm()

    return render(request,'account/signup.html', {'form': form})


def login(request):
    
    return render(request,'account/login.html')
