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
from django.contrib.auth import authenticate, logout
from django.contrib.auth import login as auth_login
from django.core.mail import EmailMessage
from homepage.tokens import account_activation_token
from homepage.forms import SignupForm,UserProfileForm, LoginForm, ResetPasswordForm, EmailInputForm
from homepage.models import UserProfile


def get_account_nav(user):
    '''Return the header navigation text based on if the user is logged in or not.

    Keyword arguments:
    user -- the user object attached to the request
    '''
    if user.is_authenticated:
        account_nav = f'hi {str(user)}, logout?'.upper()
    else:
        account_nav = 'LOGIN'
    
    return account_nav


def homepage(request):
    '''Renders the homepage view ('/') with needed context.
    
    Keyword arguments:
    request -- the http request tied to the users session
    '''
    context = {'account_nav': get_account_nav(request.user)}
    return render(request, 'homepage/homepage.html', context)
  
  
def activate(request, uidb64, token):
    '''Activates the user associated with the uidb64 and token and displays a success/error message ('/activate/<uidb64>/<token>').
    
    Keyword arguments:
    request -- the http request tied to the users session
    uidb64 -- the encoded user id
    token -- the token consisting of the userid, timestamp, and user.is_active bool hashed
    '''
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

        user.save()
        
        auth_login(request, user)
        
        context = {
            'account_nav': get_account_nav(request.user),
            'page_title': 'Notice',
            'message_title': 'Notice',
            'message_text': [f'Hello {request.user},','Your account has been activated!'],
        }
        
        return render(request,'message/message.html', context)
    else:
        context = {
            'account_nav': get_account_nav(request.user),
            'page_title': 'Notice',
            'message_title': 'Notice',
            'message_text': ['The activation link is invalid'],
        }
        
        return render(request,'message/message.html', context)
        
        
def signup(request):
    '''Renders the signup form view ('/signup') with needed context and sends a confirmation email if successful.
    
    Keyword arguments:
    request -- the http request tied to the users session
    '''
    if request.method == 'POST':
        form = SignupForm(request.POST) 
        profile_form = UserProfileForm(request.POST)
        
        if form.is_valid() and profile_form.is_valid():   #validation of both forms
            
                            # Deactivate account till it is confirmed
            user = form.save(commit=False)                      #return user from the form save
            user.is_active = False  
            user.save()
            profile=profile_form.save(commit=False) # creating new profile using data from form
            profile.user = user                     # onetoonefield relationship works here
            
            profile.save()                          # save the user 

            current_site = get_current_site(request)
            subject = 'Please Activate Your Account'
            message = render_to_string('account/account_activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(subject,message,to=[to_email])
            email.send(fail_silently=False) 
            
            context = {
                'account_nav': get_account_nav(request.user),
                'page_title': 'Notice',
                'message_title': 'Notice',
                'message_text': [f'Activation link sent to {to_email}! Please check your email and activate your account.'],
            }
            return render(request, 'message/message.html', context)
          
    else: 
        form = SignupForm()
        profile_form = UserProfileForm()


    context={'forms': [form, profile_form], 
             'page_title': 'Sign Up',
             'form_title': 'Sign Up',
             'submit_value': 'Register Account',
             'additional_html': 'account/signup_extra.html',
             'account_nav': 'SIGN-UP',
    }
    return render(request,'form/form.html', context)


def login(request):
    '''Renders the login form view ('/login') with needed context and logs the user out if they are already logged in.
    
    Keyword arguments:
    request -- the http request tied to the users session
    '''
    if request.method == 'POST':
        form = LoginForm(request.POST)
        
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            
            auth_login(request, authenticate(request, username=username, password=password))
            
            if form.cleaned_data.get('remember_me') == False:
                request.session.set_expiry(0)
            
            return redirect('/')
            
    elif request.user.is_authenticated:
        logout(request)
        form = LoginForm()
    else:
        form = LoginForm()
        
    context = {'forms': [form], # A list of all forms used
               'page_title': 'Login',
               'form_title': 'Login', # The title at the top of the form
               'submit_value': 'Login', # The value on the button for the form
               'additional_html': 'account/login_extra.html', # Additional html to be placed under the button
               'account_nav': get_account_nav(request.user), # Fills in the header 'Sign-In/Up' link
    }
    return render(request,'form/form.html', context)
  
  
def tnc(request):
    '''Renders the terms and conditions view ('/tnc') with needed context.
    
    Keyword arguments:
    request -- the http request tied to the users session
    '''
    context = {'account_nav': get_account_nav(request.user),}
    return render(request, 'tnc/tnc.html', context)
  
  
def reset_password(request, uidb64, token):
    '''Renders reset password form view ('/reset-password/<uidb64>/<token>') for the user associated with the uidb64 and token and displays a success/error message.
    
    Keyword arguments:
    request -- the http request tied to the users session
    uidb64 -- the encoded user id
    token -- the token consisting of the userid, timestamp, and user.is_active bool hashed
    '''
    User = get_user_model()
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    # checking if the user exists, if the token is valid.
    if user is not None and account_activation_token.check_token(user, token):
        if request.method == 'POST':
            form = ResetPasswordForm(request.POST)
            
            if form.is_valid():
                user.set_password(form.cleaned_data.get('password1'))
                user.save()
                
                context = {
                    'account_nav': get_account_nav(request.user),
                    'page_title': 'Notice',
                    'message_title': 'Notice',
                    'message_text': ['Account password reset'],
                }
        
                return render(request,'message/message.html', context)
                
        else:
            form = ResetPasswordForm()
            
        context = {'forms': [form], # A list of all forms used
                   'page_title': 'Reset Password',
                   'form_title': 'Reset Password', # The title at the top of the form
                   'submit_value': 'Reset Password', # The value on the button for the form
                   'additional_html': None, # Additional html to be placed under the button
                   'account_nav': get_account_nav(request.user), # Fills in the header 'Sign-In/Up' link
        }
        return render(request,'form/form.html', context)
    else:
        context = {
            'account_nav': get_account_nav(request.user),
            'page_title': 'Notice',
            'message_title': 'Notice',
            'message_text': ['The URL/token is invalid']
        }
        
        return render(request,'message/message.html', context)


def email_input(request):
    '''Renders the email input form view for resetting passwords ('/email-input') with needed context.
    
    Keyword arguments:
    request -- the http request tied to the users session
    '''
    if request.method == 'POST':
        form = EmailInputForm(request.POST)
        
        if form.is_valid():
            user_email = form.cleaned_data.get('email')
            
            current_site = get_current_site(request)
            user = User.objects.get(email=user_email)
            subject = 'Reset Password Link'
            message = render_to_string('account/reset_password_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            
            email = EmailMessage(subject,message,to=[user_email])
            email.send(fail_silently=False) 
            
            context = {
                'account_nav': get_account_nav(request.user),
                'page_title': 'Notice',
                'message_title': 'Notice',
                'message_text': [f'Reset password link sent to {user_email}! Please check your email to reset your password.']
            }
            return render(request, 'message/message.html', context)
    else:
        form = EmailInputForm()
    
    context = {'forms': [form], # A list of all forms used
               'page_title': 'Input Email',
               'form_title': 'Input Email', # The title at the top of the form
               'submit_value': 'Send Reset Link', # The value on the button for the form
               'additional_html': None, # Additional html to be placed under the button
               'account_nav': get_account_nav(request.user), # Fills in the header 'Sign-In/Up' link
    }
    return render(request,'form/form.html', context)
            