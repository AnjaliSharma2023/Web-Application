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
from homepage.forms import SignupForm,UserProfileForm, LoginForm, ResetPasswordForm, EmailInputForm, GlucoseReadingForm, CarbReadingForm,InsulinReadingForm, UpdateProfile
from homepage.models import UserProfile, Glucose, Carbohydrate, Insulin
from django.db.models import Avg, Min, Max
from datetime import date, timedelta, datetime
from django.http import JsonResponse
import pandas as pd
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication, SessionAuthentication

from homepage.serializers import GlucoseSerializer,CarbohydrateSerializer,InsulinSerializer
from rest_framework import mixins
from rest_framework import generics
#from rest_framework.schemas.coreapi import AutoSchema
import coreapi
import coreschema


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
            
            user = form.save(commit=False)          #return user from the form save
            user.is_active = False                  # Deactivate account till it is confirmed 
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
  

def logout_request(request):
    '''Logout the user and displays the message with needed context.
    
    Keyword arguments:
    request -- the http request tied to the users session
    '''
    logout(request)
    #messages.info(request, "You have successfully logged out.") 
    #return redirect("/login")
    context = {
        'account_nav': get_account_nav(request.user),
        'page_title': 'Notice',
        'message_title': 'Notice',
        'message_text': ["You have successfully logged out."]}
            
    return render(request,'message/message.html', context)

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
                'message_text': [f'Reset password link sent to {user_email}',' Please check your email to reset your password.']
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
            


@login_required
def glucose_input(request):
    '''Renders the glucose reading form view ('/glucose-input') with needed context and dispalys the message for the logged in user.

    Keyword arguments:
    request -- the http request tied to the users session
    '''

    form = GlucoseReadingForm()

    if request.method == 'POST':

        form = GlucoseReadingForm(request.POST)
        if form.is_valid():
            profile=form.save(commit=False) 
            profile.user = request.user  
            profile.save()
            #return redirect('/')
            context = {
                    'account_nav': get_account_nav(request.user),
                    'page_title': 'Notice',
                    'message_title': 'Notice',
                    'message_text': ['Glucose value saved'],
                }
        
            return render(request,'message/message.html', context)
    else:
        form = GlucoseReadingForm()

    context = {'forms': [form], # A list of all forms used
            'page_title': 'Glucose',
            'form_title': 'Glucose', # The title at the top of the form
            'submit_value': 'Submit', # The value on the button for the form
            'additional_html': 'account/glucose.html', # Additional html to be placed under the button
            'account_nav': get_account_nav(request.user),
}
    return render(request,'form/form.html', context)

@login_required
def carbs_input(request):
    '''Renders the carbs reading form view ('/carbs-input') with needed context for the logged in user.

    Keyword arguments:
    request -- the http request tied to the users session
    '''


    form = CarbReadingForm()

    if request.method == 'POST':

        form = CarbReadingForm(request.POST)
        if form.is_valid():
            profile=form.save(commit=False) 
            profile.user = request.user  
            profile.save()
            
            context = {
                    'account_nav': get_account_nav(request.user),
                    'page_title': 'Notice',
                    'message_title': 'Notice',
                    'message_text': ['Carbs value saved'],
                }
        
            return render(request,'message/message.html', context)

            
    else:
        form = CarbReadingForm()

    context = {'forms': [form], # A list of all forms used
        'page_title': 'Carbs',
        'form_title': 'Carbs', # The title at the top of the form
        'submit_value': 'Submit', # The value on the button for the form
        'additional_html': 'account/carbs.html', # Additional html to be placed under the button
        'account_nav': get_account_nav(request.user),
}
    return render(request,'form/form.html', context)

@login_required
def insulin_input(request):
    '''Renders the insulin reading form view ('/insulin-input') with needed context for the logged in user.

    Keyword arguments:
    request -- the http request tied to the users session
    '''


    form = InsulinReadingForm()

    if request.method == 'POST':

        form = InsulinReadingForm(request.POST)
        if form.is_valid():
            profile=form.save(commit=False) 
            profile.user = request.user  
            profile.save()
            
            context = {
                    'account_nav': get_account_nav(request.user),
                    'page_title': 'Notice',
                    'message_title': 'Notice',
                    'message_text': ['Insulin value saved'],
                }
        
            return render(request,'message/message.html', context)
    else:
        form = InsulinReadingForm()
    context = {'forms': [form], # A list of all forms used
        'page_title': 'Insulin',
        'form_title': 'Insulin', # The title at the top of the form
        'submit_value': 'Submit', # The value on the button for the form
        'additional_html': 'account/insulin.html', # Additional html to be placed under the button
        'account_nav': get_account_nav(request.user),
}
    return render(request,'form/form.html', context)
    
@login_required
def dashboard(request):
    '''Renders the dashboard view ('/dashboard2/index') with needed context.
    
    Keyword arguments:
    request -- the http request tied to the users session
    '''
    context = {'username': str(request.user)}
    return render(request, 'dashboard2/index.html', context)

def dashboard_data(request, start_date, end_date):
    '''Renders the dashboard data form view ('/dashboard-data/<start_date>/<end_date>/') with the different plot description for the logged in user.

    Keyword arguments:
    request -- the http request tied to the users session
    start_date -- the selected start date as an iso formatted string
    end_date -- the selected end date as an iso formatted string
    '''

    start_date = datetime.fromisoformat(start_date)
    end_date = datetime.fromisoformat(end_date) + timedelta(days=1)
    
    # Solid gauge data
    avg_glucose = Glucose.objects.filter(user=request.user,record_datetime__date__gt=start_date,record_datetime__date__lt=end_date).aggregate(Avg('glucose_reading')).get('glucose_reading__avg')
    min_glucose = Glucose.objects.filter(user=request.user,record_datetime__date__gt=start_date,record_datetime__date__lt=end_date).aggregate(Min('glucose_reading')).get('glucose_reading__min')
    max_glucose = Glucose.objects.filter(user=request.user,record_datetime__date__gt=start_date,record_datetime__date__lt=end_date).aggregate(Max('glucose_reading')).get('glucose_reading__max')
    
    if avg_glucose != None:
        avg_glucose = int(avg_glucose)
        a1c = round(((avg_glucose +  46.7)/ 28.7),2)
    else:
        a1c = 0
        avg_glucose = 0
        min_glucose = 0
        max_glucose = 0
    
    # Last input data
    last_glucose = Glucose.objects.filter(user=request.user).aggregate(Max('record_datetime')).get('record_datetime__max')
    last_carb = Carbohydrate.objects.filter(user=request.user).aggregate(Max('record_datetime')).get('record_datetime__max')
    last_insulin = Insulin.objects.filter(user=request.user).aggregate(Max('record_datetime')).get('record_datetime__max')
    
    if last_glucose is None:
        last_glucose = ''
    else:
        last_glucose = last_glucose.date().strftime('%B %d, %Y')
        
    if last_carb is None:
        last_carb = ''
    else:
        last_carb = last_carb.date().strftime('%B %d, %Y')
        
    if last_insulin is None:
        last_insulin = ''
    else:
        last_insulin = last_insulin.date().strftime('%B %d, %Y')
        
    # Scatter/bar plot data
    insulin_objects = Insulin.objects.filter(user=request.user,record_datetime__gt=start_date, record_datetime__lt=end_date)
    carbohydrate_objects = Carbohydrate.objects.filter(user=request.user,record_datetime__gt=start_date, record_datetime__lt=end_date)
    
    min_dosage = 0
    max_dosage = Insulin.objects.filter(user=request.user,record_datetime__date__gt=start_date,record_datetime__date__lt=end_date).aggregate(Max('dosage')).get('dosage__max')
    min_carbs = 0
    max_carbs = Carbohydrate.objects.filter(user=request.user,record_datetime__date__gt=start_date,record_datetime__date__lt=end_date).aggregate(Max('carb_reading')).get('carb_reading__max')
    
    if max_dosage == None:
        max_dosage = 6
    else:
        max_dosage = int(max_dosage + 2)
        
    if max_carbs == None:
        max_carbs = 30
    else:
        max_carbs = int(max_carbs + 5)
    
    insulin_data = []
    carbohydrate_data = []
    for item in carbohydrate_objects:
        carbohydrate_data.append([item.record_datetime.timestamp()*1000, item.carb_reading])
        
    for item in insulin_objects:
        insulin_data.append([item.record_datetime.timestamp()*1000, item.dosage])
        
    min_time = start_date.timestamp() * 1000
    max_time = end_date.timestamp() * 1000
    
    plotlines = []
    for day in pd.date_range(start=start_date,end=end_date).to_pydatetime():
        plotlines.append(day.timestamp() * 1000)
    
    # Carb percent in range data
    bar_data_carbs = {'Day': {'inrange':0, 'aboverange':0}}
    for day in pd.date_range(start=start_date,end=end_date).to_pydatetime():
        carb_objects = Carbohydrate.objects.filter(user=request.user, record_datetime__gt=day, record_datetime__lt=day + timedelta(days=1))
        carb_day_total = 0
        for item in carb_objects:
            carb_day_total += item.carb_reading
            
            if carb_day_total > 325:
                bar_data_carbs['Day']['aboverange'] += 1
            else:
                bar_data_carbs['Day']['inrange'] += 1
                
    bar_plot_carbs = {'data':[]}
    inrange = {'name': 'In-range (0-325)', 'color': '#8CC63E','data':[]}
    aboverange = {'name': 'Above-range (>325)', 'color':'#7069AF', 'data':[]}
    for section, value in bar_data_carbs.items():
        total = value['aboverange'] + value['inrange']
        if total == 0:
            total = 1
            
        inrange['data'].append(value['inrange']/total*100)
        aboverange['data'].append(value['aboverange']/total*100)
    
    bar_plot_carbs['data'].append(aboverange)
    bar_plot_carbs['data'].append(inrange)
    
    # Glucose percent in range and glucose whisker plot data
    glucose_objects = Glucose.objects.filter(user=request.user,record_datetime__gt=start_date, record_datetime__lt=end_date)
    box_data = {'Night':{'items':[]},'Morning':{'items':[]},'Afternoon':{'items':[]},'Evening':{'items':[]}}
    bar_data_glucose = {'Night': {'inrange':0, 'belowrange':0, 'aboverange':0}, 'Morning': {'inrange':0, 'belowrange':0, 'aboverange':0}, 'Afternoon': {'inrange':0, 'belowrange':0, 'aboverange':0}, 'Evening': {'inrange':0, 'belowrange':0, 'aboverange':0}}
    for item in glucose_objects: 
        if item.record_datetime.hour < 6:
            # Box plot code
            box_data['Night']['items'].append(item)
            # Bar chart code
            if item.glucose_reading < 80:
                bar_data_glucose['Night']['belowrange'] += 1
            elif item.glucose_reading > 160:
                bar_data_glucose['Night']['aboverange'] += 1
            else:
                bar_data_glucose['Night']['inrange'] += 1
                
        elif item.record_datetime.hour < 12:
            # Box plot code
            box_data['Morning']['items'].append(item)
            # Bar chart code
            if item.glucose_reading < 80:
                bar_data_glucose['Morning']['belowrange'] += 1
            elif item.glucose_reading > 160:
                bar_data_glucose['Morning']['aboverange'] += 1
            else:
                bar_data_glucose['Morning']['inrange'] += 1
        elif item.record_datetime.hour < 18:
            # Box plot code
            box_data['Afternoon']['items'].append(item)
            # Bar chart code
            if item.glucose_reading < 80:
                bar_data_glucose['Afternoon']['belowrange'] += 1
            elif item.glucose_reading > 160:
                bar_data_glucose['Afternoon']['aboverange'] += 1
            else:
                bar_data_glucose['Afternoon']['inrange'] += 1
        else:
            # Box plot code
            box_data['Evening']['items'].append(item)
            # Bar chart code
            if item.glucose_reading < 80:
                bar_data_glucose['Evening']['belowrange'] += 1
            elif item.glucose_reading > 160:
                bar_data_glucose['Evening']['aboverange'] += 1
            else:
                bar_data_glucose['Evening']['inrange'] += 1
    
    # Glucose in range code
    bar_plot_glucose = {'data':[]}
    inrange = {'name': 'In-range (80-160)', 'color': '#8CC63E','data':[]}
    aboverange = {'name': 'Above-range (>160)', 'color':'#7069AF', 'data':[]}
    belowrange = {'name': 'Below-range (<80)', 'color':'#fab3c4', 'data':[]}
    for section, value in bar_data_glucose.items():
        total = value['inrange'] + value['belowrange'] + value['aboverange']
        if total == 0:
            total = 1
            
        inrange['data'].append(value['inrange']/total*100)
        aboverange['data'].append(value['aboverange']/total*100)
        belowrange['data'].append(value['belowrange']/total*100)
        
    bar_plot_glucose['data'].append(aboverange)
    bar_plot_glucose['data'].append(inrange)
    bar_plot_glucose['data'].append(belowrange)
    
    # Box plot code
    box_plot = {}
    box_plot['data'] = []
    box_plot['outliers'] = []
    index = 0
    for section, value in box_data.items():
        
        ordered = [item.glucose_reading for item in value['items']]
        ordered.sort()
        len_items = len(ordered)
        if len_items == 0:
            box_plot['data'].append([])
            continue
        
        if len_items % 2 != 0: # Odd
            box_data[section]['Q2'] = ordered[len_items // 2]
        else:
            box_data[section]['Q2'] = (ordered[len_items // 2] + ordered[len_items // 2 - 1]) / 2
            
        len_items_half = len_items // 2
        if len_items_half % 2 != 0:
            box_data[section]['Q1'] = ordered[len_items_half // 2]
            box_data[section]['Q3'] = ordered[-(len_items_half // 2 + 1)]
        else:
            box_data[section]['Q1'] = (ordered[len_items_half // 2] + ordered[len_items_half // 2 - 1]) / 2
            box_data[section]['Q3'] = (ordered[-(len_items_half // 2 + 1)] + ordered[-(len_items_half // 2)]) / 2
        
        iqr = box_data[section]['Q3'] - box_data[section]['Q1']
        box_data[section]['lower limit'] = box_data[section]['Q1'] - 1.5 * iqr
        box_data[section]['upper limit'] = box_data[section]['Q3'] + 1.5 * iqr
        
        for item in value['items']:
            if item.glucose_reading < box_data[section]['lower limit'] or item.glucose_reading > box_data[section]['upper limit']:
                box_plot['outliers'].append([index, item.glucose_reading])
        
        box_plot['data'].append([box_data[section]['lower limit'], box_data[section]['Q1'], box_data[section]['Q2'], box_data[section]['Q3'], box_data[section]['upper limit']])
        
        index += 1
    
    dashboard_data = {'last_glucose': last_glucose, 'last_carb': last_carb, 'last_insulin': last_insulin, 'progress_circles': {'min': min_glucose, 'max': max_glucose, 'avg': avg_glucose, 'hba1c': a1c}, 'scatter_bar_plot': {'min_dosage':min_dosage, 'max_dosage':max_dosage, 'min_carbs': min_carbs, 'max_carbs': max_carbs, 'min_time': min_time, 'max_time': max_time, 'plotlines': plotlines, 'insulin_data': insulin_data, 'carbohydrate_data': carbohydrate_data}, 'box_plot':box_plot, 'bar_plot_glucose':bar_plot_glucose, 'bar_plot_carbs': bar_plot_carbs}
    
    return JsonResponse(dashboard_data)
    
@login_required
def analytics_data(request): # start_date, end_date
    #start_date = datetime.fromisoformat(start_date)
    #end_date = datetime.fromisoformat(end_date) + timedelta(days=1)
    
    start_date = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=30)
    end_date = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
    
    glucose_objects = Glucose.objects.filter(user=request.user, record_datetime__gt=start_date, record_datetime__lt=end_date)
    print(len(glucose_objects))
    #mealtime_ranges = { 'breakfast': [6,8],
    #    'inbetween1': [9,10],
    #    'lunch': [11,13],
    #    'inbetween2': [14,16],
    #    'dinner': [17,20],
    #    'bedtime': [21,25]}
    group_hour_ranges = [[[6,9], [11,14]], [[11,14], [17,21]], [[17,21], [21,26]]]
    glucose_grouped = [[] for x in range(3)]
    for day in pd.date_range(start=start_date, end=end_date).to_pydatetime():
        days_readings = glucose_objects.filter(record_datetime__gt=day+timedelta(hours=2), record_datetime__lt=day+timedelta(days=1, hours=2))
        for reading in days_readings:
            indexes = group_data(day, group_hour_ranges, reading.record_datetime)
            if type(indexes) is tuple:
                for index in indexes:
                    glucose_grouped[index].append(reading)
            else:
                glucose_grouped[indexes].append(reading)
    
    for group in glucose_grouped:
        print('\nNew Group')
        for item in group:
            print(f'{item.record_datetime}: {item.glucose_reading}')
    
    determine_trends(glucose_grouped[0])
    
    return JsonResponse({'group1':0})


def determine_trends(data_group):
    statements = [['normal_glucose', 0], ['up_basal', 0], ['down_basal', 0], ['up_bolus', 0], ['down_bolus', 0], ['earlier_bolus', 0], ['normal_carbs', 0], ['lower_daily_carbs', 0], ['lower_mealtime_carbs', 0]]
    trends = {statements[0][0]:{'x,=,x+-10':1}, statements[1][0]:{'1.5x,>,x+-10,x+20/25,>,1:30':1, 'x,>,x+30/50':.5}, statements[2][0]:{'1.5x,<,x+-10,x-20/25,>,1:30':1, 'x,<,40/80,>,1:30':.5, 'x,<,x-30/50':.5}, 
        statements[3][0]:{'x,>,x+15/25,>,1:30':1, 'x,>,x+30/50':.5}, statements[4][0]:{'x,<,40/80,<,1:30':1, 'x,<,x-15/25,>,1:30':1, 'x,<,40/80,>,1:30':.5, 'x,<,x-30/50':.5}, 
        statements[5][0]:{'x,>,x+50/80,x+-15,<,1:30':1}, statements[6][0]:{'x,=,0/85':1}, statements[7][0]:{'x,>,275/300,=,24:00':1}, statements[8][0]:{'x,>,90/100':1}}
    
    if all(type(x) is Glucose for x in data_group):
        for statement in statements[-3:]:
            del trends[statement[0]]
        statements = statements[:-3]
    elif all(type(x) is Carbohydrate for x in data_group):
        for statement in statements[:-3]:
            del trends[statement[0]]
        statements = statements[-3:]
    else:
        raise ValueError('Mixed data types received, expected an iterator with either Glucose or Carbohydrate objects')
            
    print()
    print(statements)
    print()
    print(trends)
    
def group_data(day, group_hour_ranges, record_datetime):
    for index in range(len(group_hour_ranges)):
        if group_hour_ranges[index][0][0] <= record_datetime.hour < group_hour_ranges[index][1][0]:
            return index
        elif (group_hour_ranges[index][1][0] <= record_datetime.hour < group_hour_ranges[index][1][1]) and index != 2:
            print(f'{record_datetime}: {index, index+1}')
            return index, index + 1
        else:
            if group_hour_ranges[index][1][1] > 24:
                start_time = day.replace(hour=group_hour_ranges[index][1][0], minute=0, second=0, microsecond=0)
                end_time = day.replace(hour=23, minute=0, second=0, microsecond=0) + timedelta(hours=group_hour_ranges[index][1][1]-23)
                comp_time = record_datetime
            else:
                start_time = group_hour_ranges[index][1][0]
                end_time = group_hour_ranges[index][1][1]
                comp_time = record_datetime.hour
                
            if start_time <= comp_time < end_time:
                return index
    
    print(day, record_datetime)
    raise IndexError("Could not place reading into a range")
            
            

@login_required
def profile_page(request):
    '''Renders the profile page form view ('/profile-page') with needed context for the logged in user to view and edit profile.

    Keyword arguments:
    request -- the http request tied to the users session
    '''

    if request.method == 'POST':
        form = UpdateProfile(request.POST,instance=request.user) 
        profile_form = UserProfileForm(request.POST,instance=UserProfile.objects.get(user=request.user))
        
        if form.is_valid() and profile_form.is_valid():  
                   
            user = form.save(commit=False)          #return user from the form save
                         
            user.save()
            profile=profile_form.save(commit=False) # creating new profile using data from form
            profile.user = user                     # onetoonefield relationship works here
            
            profile.save()        
                           
            #return redirect('profile_page')
            context = {
                    'account_nav': get_account_nav(request.user),
                    'page_title': 'Notice',
                    'message_title': 'Notice',
                    'message_text': ['Your profile is successfully updated'],
                }
        
            return render(request,'message/message.html', context)
    else:
    
        form = UpdateProfile(instance=request.user)
        profile_form = UserProfileForm(instance=UserProfile.objects.get(user=request.user))


    context={'forms': [form, profile_form], 
            'page_title': 'Profile',
            'form_title': 'Profile',
            'submit_value': 'Update',
            'additional_html': 'account/profile.html',
            'account_nav': get_account_nav(request.user),
    }
    return render(request,'form/form.html', context)


class GlucoseView(mixins.ListModelMixin,
                  mixins.CreateModelMixin,
                  generics.GenericAPIView):
    """ 
    ---
    get:
        Return the last 4 entries by the user.
        
    post:
        Create a new entry of Glucose.
        Unit for glucose_reading = mg/dl and
        it should be between 0 and 400.

    """ 
    
    queryset = Glucose.objects.all().order_by('-id')[:3]
    serializer_class = GlucoseSerializer
    permission_classes = (IsAuthenticated,)
        

    def get(self, request, *args, **kwargs):
     
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

class CarbsView(mixins.ListModelMixin,
                  mixins.CreateModelMixin,
                  generics.GenericAPIView):
    """ 
    ---
    get:
        Return the last 4 entries by the user.
        
    post:
        Create a new entry of Carbohydrate.
        Carbohydrate reading should be between 0 and 300.

    """ 
    
    queryset = Carbohydrate.objects.all().order_by('-id')[:3]
    serializer_class = CarbohydrateSerializer
    permission_classes = (IsAuthenticated,)
    

    def get(self, request, *args, **kwargs):
     
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
    


class InsulinAPIView(mixins.ListModelMixin,
                  mixins.CreateModelMixin,
                  generics.GenericAPIView):
    """ 
    ---
    get:
        Return the last 4 entries by the user.
        
    post:
        Create a new entry of Insulin.
        Insulin dosage should be between 0 and 50.

    """ 

    queryset = Insulin.objects.all().order_by('-id')[:3]
    serializer_class = InsulinSerializer
    permission_classes = (IsAuthenticated,)


    def get(self, request, *args, **kwargs):
     
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
    
    