from django.utils.encoding import force_text
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import login, authenticate,logout
from django.core.mail import EmailMessage

from .tokens import account_activation_token
from .forms import SignupForm,UserProfileForm, LoginForm

from .models import UserProfile

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

def activation_sent_view(request):
    return render(request, 'account/activation_sent.html')
    
def activate(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    # checking if the user exists, if the token is valid.
    if user is not None and account_activation_token.check_token(user, token):
        # if valid set active true 
        user.is_active = True
        # set signup_confirmation true
        UserProfile.signup_confirmation = True
        user.save()
        #login(request,user)
        
        return render(request,'account/account_activation_email.html')
    else:
        return HttpResponse('Activation link is invalid!')
        #return redirect('/')
    #else:
    #     return render(request, 'activation_invalid.html')

def signup(request):

    if request.method == 'POST':
        form = SignupForm(request.POST) 
        profile_form = UserProfileForm(request.POST)
        
        if form.is_valid() and profile_form.is_valid():   #validation of both forms
            
            user = form.save() #return user from the form save
      
            # creating new profile using data from form
            profile=profile_form.save(commit=False) 
            profile.user = user  # onetoonefield relationship works here
            
            user.is_active = False

            
            profile.save() # save the user 

            current_site = get_current_site(request)
            subject = 'Please Activate Your Account'
            message = render_to_string('account/account_activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            #to_email = form.cleaned_data.get('email')
            
            user.email_user(subject, message)
            
            #username = form.cleaned_data.get('username') #clean the data
            #password = form.cleaned_data.get('password1')  
            #user = authenticate(username = username, password = password)  
            messages.success(request,"Account created successfully: {username}")       
            #login(request,user)
            #return redirect('activation_sent')
            #return redirect('login')
    else: 
        form = SignupForm()
        profile_form = UserProfileForm()


    context={'forms': [form, profile_form], 
             'form_title': 'Sign Up',
             'submit_value': 'Register Account',
             'additional_html': 'account/signup_extra.html',
             'username': 'Sign-In/Up',
             'active': 'Sign-In/Up'}
    return render(request,'account/signupNEW.html', context)


def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        
        if form.is_valid():
            username = form.cleaned_data.get('username')
            user = authenticate(username = username, password = form.cleaned_data.get('password'))
            if user is not None:
                print(UserProfile.objects.raw(f'select signup_confirmation from homepage_userprofile where user_id={username}'))
                if UserProfile.objects.raw(f'select signup_confirmation from homepage_userprofile where user_id={username}'):
                    login(request, user)
                    return redirect('/')
                else:
                    messages.info(request, 'Your account is not authenticated')
                
            else:
                messages.info(request, 'Username OR password is incorrect')
                
            request.user
            
            return redirect("")
    else:
        form = LoginForm()
        
    context = {'forms': [form], # A list of all forms used
               'form_title': 'Login', # The title at the top of the form
               'submit_value': 'Login', # The value on the button for the form
               'additional_html': 'account/login_extra.html', # Additional html to be placed under the button
               'username': 'Sign-In/Up', # Fills in the header 'Sign-In/Up' link
               'active': 'Sign-In/Up', # tell which tab is being displayed for different coloring
    }
    return render(request,'account/loginNEW.html', context)