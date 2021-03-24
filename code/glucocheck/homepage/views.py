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
            


@login_required
def glucose_input(request):

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
                    'message_text': ['Value saved.'],
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
                    'message_text': ['Value saved.'],
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
                    'message_text': ['Value saved.'],
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
    context = {}
    return render(request, 'dashboard2/index.html', context)

def dashboard_data(request, start_date, end_date):
    # Scatter plot code is commented out
    start_date = datetime.fromisoformat(start_date)
    end_date = datetime.fromisoformat(end_date) + timedelta(days=1)

    avg_glucose = Glucose.objects.filter(user=request.user,record_datetime__date__gt=start_date,record_datetime__date__lt=end_date).aggregate(Avg('glucose_reading')).get('glucose_reading__avg')
    min_glucose = Glucose.objects.filter(user=request.user,record_datetime__date__gt=start_date,record_datetime__date__lt=end_date).aggregate(Min('glucose_reading')).get('glucose_reading__min')
    max_glucose = Glucose.objects.filter(user=request.user,record_datetime__date__gt=start_date,record_datetime__date__lt=end_date).aggregate(Max('glucose_reading')).get('glucose_reading__max')
    
    last_glucose = Glucose.objects.filter(user=request.user,record_datetime__date__gt=start_date,record_datetime__date__lt=end_date).aggregate(Max('record_datetime')).get('record_datetime__max')
    last_carb = Carbohydrate.objects.filter(user=request.user,record_datetime__date__gt=start_date,record_datetime__date__lt=end_date).aggregate(Max('record_datetime')).get('record_datetime__max')
    last_insulin = Insulin.objects.filter(user=request.user,record_datetime__date__gt=start_date,record_datetime__date__lt=end_date).aggregate(Max('record_datetime')).get('record_datetime__max')
    
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
        
    
    if avg_glucose != None:
        avg_glucose = int(avg_glucose)
        a1c = round(((avg_glucose +  46.7)/ 28.7),2)
    else:
        a1c = 0
        avg_glucose = 0
        min_glucose = 0
        max_glucose = 0
        
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
    
    glucose_objects = Glucose.objects.filter(user=request.user,record_datetime__gt=start_date, record_datetime__lt=end_date)
    #data = []
    box_data = {'Night':{'items':[]},'Morning':{'items':[]},'Afternoon':{'items':[]},'Evening':{'items':[]}}
    bar_data_glucose = {'Night': {'inrange':0, 'belowrange':0, 'aboverange':0}, 'Morning': {'inrange':0, 'belowrange':0, 'aboverange':0}, 'Afternoon': {'inrange':0, 'belowrange':0, 'aboverange':0}, 'Evening': {'inrange':0, 'belowrange':0, 'aboverange':0}}
    for item in glucose_objects:
        #data.append([item.record_datetime.timestamp()*1000, item.glucose_reading])
        
        # Box plot code
        if item.record_datetime.hour < 6:
            box_data['Night']['items'].append(item)
            # Bar chart code
            if item.glucose_reading < 80:
                bar_data_glucose['Night']['belowrange'] += 1
            elif item.glucose_reading > 160:
                bar_data_glucose['Night']['aboverange'] += 1
            else:
                bar_data_glucose['Night']['inrange'] += 1
                
        elif item.record_datetime.hour < 12:
            box_data['Morning']['items'].append(item)
            # Bar chart code
            if item.glucose_reading < 80:
                bar_data_glucose['Morning']['belowrange'] += 1
            elif item.glucose_reading > 160:
                bar_data_glucose['Morning']['aboverange'] += 1
            else:
                bar_data_glucose['Morning']['inrange'] += 1
        elif item.record_datetime.hour < 18:
            box_data['Afternoon']['items'].append(item)
            # Bar chart code
            if item.glucose_reading < 80:
                bar_data_glucose['Afternoon']['belowrange'] += 1
            elif item.glucose_reading > 160:
                bar_data_glucose['Afternoon']['aboverange'] += 1
            else:
                bar_data_glucose['Afternoon']['inrange'] += 1
        else:
            box_data['Evening']['items'].append(item)
            # Bar chart code
            if item.glucose_reading < 80:
                bar_data_glucose['Evening']['belowrange'] += 1
            elif item.glucose_reading > 160:
                bar_data_glucose['Evening']['aboverange'] += 1
            else:
                bar_data_glucose['Evening']['inrange'] += 1
    
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
    
    min_time = start_date.timestamp() * 1000
    max_time = end_date.timestamp() * 1000
    
    plotlines = []
    for day in pd.date_range(start=start_date,end=end_date).to_pydatetime():
        plotlines.append(day.timestamp() * 1000)
    
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
    #scatter_plot = {
    #    'data':data,
    #    'plotlines': plotlines,
    #    
    #}
    dashboard_data = {'last_glucose': last_glucose, 'last_carb': last_carb, 'last_insulin': last_insulin, 'progress_circles': {'min': min_glucose, 'max': max_glucose, 'avg': avg_glucose, 'hba1c': a1c}, 'scatter_bar_plot': {'min_dosage':min_dosage, 'max_dosage':max_dosage, 'min_carbs': min_carbs, 'max_carbs': max_carbs, 'min_time': min_time, 'max_time': max_time, 'plotlines': plotlines, 'insulin_data': insulin_data, 'carbohydrate_data': carbohydrate_data}, 'box_plot':box_plot, 'bar_plot_glucose':bar_plot_glucose, 'bar_plot_carbs': bar_plot_carbs}
    
    return JsonResponse(dashboard_data)

@login_required
def profile_page(request):

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
                    'message_text': ['Your profile updated.'],
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

'''
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(data=request.POST, user=request.user )
        if form.is_valid():
            profile=form.save(commit=False) 
            profile.user = request.user  
            profile.save()
            
            update_session_auth_hash(request, profile)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            #return redirect('homepage/profile')#
            context = {
                    'account_nav': get_account_nav(request.user),
                    'page_title': 'Notice',
                    'message_title': 'Notice',
                    'message_text': ['Your password updated.'],
                }
        
            return render(request,'message/message.html', context)
        
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
        context={'forms': [form], 
            'page_title': 'Change Password',
            'form_title': 'Change Password',
            'submit_value': 'Save',
            'additional_html': None,
            'account_nav': get_account_nav(request.user),
    }
    return render(request,'form/form.html', context)
    
'''

