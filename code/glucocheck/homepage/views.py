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
        #info_form = InfoProfile(data=request.POST)
        if form.is_valid() :
            user = form.save()
            user.save()
            #profile=info_form.save(commit=False)
            #profile.user = user
            #profile.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')  
            user = authenticate(username = username, password = raw_password)         
            #login(request,user)
            messages.success(request,'Account created successfully ')
            return redirect('login')
    else: 
        form = SignupForm()
        #info_form = InfoProfile(data=request.POST)

    return render(request,'account/signup.html', {'form': form})
    #return render(request,'account/signup.html', {'form': form,'info_form':info_form})


def login(request):
    
    return render(request,'account/login.html')
