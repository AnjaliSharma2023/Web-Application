from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import SignupForm,UserProfileForm
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
        profile_form = UserProfileForm(request.POST)
        
        if form.is_valid() and profile_form.is_valid():   #validation of both forms
            user = form.save()
            user.save()
            # creating new profile using data from form
            profile=profile_form.save(commit=False) # do not save to databse now
            profile.user = user  # onetoonefield comes here
            
            profile.save() # save the user 

            username = form.cleaned_data.get('username') #clean the data
            password = form.cleaned_data.get('password1')  
            user = authenticate(username = username, password = password)  
            messages.success(request,"Account created successfully: {username}")       
            login(request,user)
            
            return redirect('login')
    else: 
        form = SignupForm()
        profile_form = UserProfileForm()

    #return render(request,'account/signup.html', {'form': form})
    #return render(request,'account/signup.html', {'form': form,'profile_form':profile_form})
        
    
    context={'form': form, 
             'profile_form':profile_form,
             'form_title': 'Sign Up',
             'submit_value': 'Register Account',
             'additional_html': 'account/signup_extra.html',
             'username': 'Sign-In/Up',
             'active': 'Sign-In/Up'}
    return render(request,'account/signupNEW.html', context)


'''def login(request):
    
    return render(request,'account/login.html')'''