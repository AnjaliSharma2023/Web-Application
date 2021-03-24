from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from homepage.models import UserProfile, Glucose, Carbohydrate, Insulin
from datetime import date, datetime
from homepage.widgets import CheckboxLink, InputWithSelector
from localflavor.us.forms import USStateSelect
from django.contrib.auth import authenticate
from homepage.fields import FloatWithUnitField, IntWithUnitField


class SignupForm(UserCreationForm):
    '''Cleans the data and handles the html display of the signup form.
    
    Public methods:
    clean_email -- ensures the inputted email is not already associated with a user
    clean -- ensures the password inputs match and adhere to the security requirements
    
    Instance variables:
    username -- a form character field for the user's username
    email -- a form email field for the user's email
    password1 -- a form character field for the user's password
    password2 -- a form character field for the user's password repeated
    '''
    username = forms.CharField(required =True, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Username'}), label='user.svg')
    email=forms.EmailField(required =True, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Email'}), label='envelope.svg')
    password1 = forms.CharField(required=True, widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'Password'}), label='key.svg')
    password2 = forms.CharField(required=True, widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'Password Confirmation'}), label='key.svg')
    
    
    class Meta:
        '''Meta data on the form.
        
        Instance variables:
        model -- the model the form relates to
        fields -- the model fields the form fields relate to
        '''
        model = User
        fields = (
            'username',
            'email',
            'password1',
            'password2',
        ) 
    
    def clean_email(self):
        '''Cleans the input email by ensuring its not already associated with a user.
    
        Keyword arguments:
        self -- the SignupForm object
        '''
        email = self.cleaned_data['email']
        
        try:
            User.objects.get(email=email)
            raise forms.ValidationError('A user with that email already exists')
        except User.DoesNotExist:
            return email
            
    def clean(self):
        '''Cleans the input passwords by ensuring they match and adhere to security standards.
    
        Keyword arguments:
        self -- the SignupForm object
        '''
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        
        uppercase = False
        lowercase = False
        number = False
        
        for letter in password1:
            if uppercase == False and letter.isupper():
                uppercase = True
            
            if lowercase == False and letter.islower():
                lowercase = True
            
            if number == False and letter.isnumeric():
                number = True
        
        if password1 == password2 and (len(password1) < 6 or uppercase == False or lowercase == False or number == False):
            raise forms.ValidationError('Your password must be at least 6 letters long and contain at least one uppercase letter, one lowercase letter, and one digit')
            

class UserProfileForm(forms.ModelForm):
    '''Cleans the data and handles the html display of the user profile form.
    
    Public methods:
    clean_birth_date -- ensures the users age is equal to or above 18 years
    
    Instance variables:
    birth_date -- a form date field for the user's birth date
    state -- a form character field for the user's state of residence
    signup_confirmation -- a boolean field to ensure the user has read and agrees to the terms and conditions
    '''
    birth_date = forms.DateField(required=True,widget = forms.DateInput(attrs={'class':'form-control', 'placeholder':'Birth Date', 'onfocus':"(this.type='date')", 'onfocusout':"(this.type='text')"}), label='calendar-alt.svg')
    state = forms.CharField(required =True, widget=USStateSelect(attrs={'class':'form-control', 'placeholder':'State'}), label='map-marker-alt.svg')
    signup_confirmation = forms.BooleanField(required =True, widget=CheckboxLink(link_text='TNC', side_text='Have you have read and agree to the ', wrap_elem='div', wrap_elem_attrs={'class':'column'}, link_attrs={'target':'_blank', 'rel':'noreferrer noopener', 'href':"../tnc/"}), label="user.svg")
    

    class Meta():
        '''Meta data on the form.
        
        Instance variables:
        model -- the model the form relates to
        fields -- the model fields the form fields relate to
        '''
        model = UserProfile
        fields = ('birth_date','state')
        
    def clean_birth_date(self):
        '''Cleans the input birth date by ensuring the user is above 18 years of age.
    
        Keyword arguments:
        self -- the UserProfileForm object
        '''
        birth_date = self.cleaned_data['birth_date']
        today = date.today()
        if (birth_date.year + 18, birth_date.month, birth_date.day) > (today.year, today.month, today.day):
            raise forms.ValidationError('Must be at least 18 years old to register')
        return birth_date
       
       
class LoginForm(forms.Form):
    '''Cleans the data and handles the html display of the login form.
    
    Public methods:
    clean -- ensures the input username and password relate to a user
    
    Instance variables:
    username -- a form character field for the user's username
    password -- a form character field for the user's password
    remember_me -- a boolean field that determines how long to keep the user's session
    '''
    username = forms.CharField(required =True, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Username'}), label='user.svg')
    password = forms.CharField(required=True, widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'Password'}), label='key.svg')
    remember_me = forms.BooleanField(required =False, widget=CheckboxLink(side_text='Remember me', wrap_elem='div', wrap_elem_attrs={'class':'column'}), label="user.svg")
    
    def clean(self):
        '''Cleans the input username and password by ensuring they relate to a user.
    
        Keyword arguments:
        self -- the LoginForm object
        '''
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        password = cleaned_data.get("password")
        
        user = authenticate(username = username, password = password)
        if user is not None:
            if user.is_active == False:
                raise forms.ValidationError('Your account is not authenticated, please click the link in your email')
        else:
            raise forms.ValidationError('Your username OR password is incorrect')
            
            
class ResetPasswordForm(forms.Form):
    '''Cleans the data and handles the html display of the reset password form.
    
    Public methods:
    clean -- ensures the input passwords match and adhere to security standards
    
    Instance variables:
    password1 -- a form character field for the user's password
    password2 -- a form character field for confirmation of the user's password
    '''
    password1 = forms.CharField(required=True, widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'New Password'}), label='key.svg')
    password2 = forms.CharField(required=True, widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'Password Confirmation'}), label='key.svg')        
    
    def clean(self):
        '''Cleans the input passwords by ensuring they match and adhere to security standards.
    
        Keyword arguments:
        self -- the ResetPasswordForm object
        '''
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        
        if password1 != password2:
            raise forms.ValidationError('The two password fields didn’t match.')
        
        uppercase = False
        lowercase = False
        number = False
        
        for letter in password1:
            if uppercase == False and letter.isupper():
                uppercase = True
            
            if lowercase == False and letter.islower():
                lowercase = True
            
            if number == False and letter.isnumeric():
                number = True
        
        if len(password1) < 6 or uppercase == False or lowercase == False or number == False:
            raise forms.ValidationError('Your password must be at least 6 letters long and contain at least one uppercase letter, one lowercase letter, and one digit')
            
        
class EmailInputForm(forms.Form):
    '''Cleans the data and handles the html display of the email input form.
    
    Public methods:
    clean_email -- ensures the input email is associated with a user
    
    Instance variables:
    email -- a form email field for the user's email
    '''
    email = forms.EmailField(required =True, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Email'}), label='envelope.svg')
    #testWidget = FloatWithUnitField(widget=InputWithSelector(forms.TextInput, [(1,'mg/dL'),(2,'mmo/L')], attrs={'placeholder':'glucose'}, wrap_elem='div', wrap_elem_attrs={'class':'column'}))
    
    
    def clean_email(self):
        '''Cleans the input email by ensuring it is associated with a user.
    
        Keyword arguments:
        self -- the EmailInputForm object
        '''
        email = self.cleaned_data['email']
        
        try:
            User.objects.get(email=email)
        except User.DoesNotExist:
            raise forms.ValidationError('This email is not associated with a user')
            
        return email
     
        
class GlucoseReadingForm(forms.ModelForm):

    categories_choices =[
        ('fasting','Fasting'),
        ('before breakfast','Before Breakfast'),
        ('after breakfast','After Breakfast'),
        ('before lunch','Before Lunch'),
        ('after lunch','After Lunch'),
        ('snacks','Snacks'),
        ('before dinner','Before Dinner'),
        ('after dinner','After Dinner'),
    ]
    
    glucose_reading = IntWithUnitField(required=True, widget=InputWithSelector(forms.NumberInput, [('mg/dL','mg/dL'),('mmo/L','mmo/L')], attrs={'placeholder':'glucose', 'class':'form-control'}, wrap_elem='div', wrap_elem_attrs={'class':'column'}))
    #glucose_reading = IntWithUnitField(required=True, widget= forms.NumberInput(attrs={'class':'form-control', 'placeholder':'Glucose Value'}))
    record_datetime = forms.DateTimeField(required=True, widget = forms.DateTimeInput(attrs={'class':'form-control', 'placeholder':'Record Datetime'}))
    notes = forms.CharField(required=False, widget= forms.Textarea(attrs={'rows': 1,'cols': 40,'class':'form-control', 'placeholder':'Notes'}))
    categories = forms.MultipleChoiceField(required=True,widget=forms.Select(attrs={'class':'form-control', 'placeholder':'Categories'}),choices=categories_choices)
    

    class Meta():
        '''Meta data on the form.
        
        Instance variables:
        model -- the model the form relates to
        fields -- the model fields the form fields relate to
        '''
        model = Glucose
        fields = ('glucose_reading','record_datetime','notes','categories')


    
    def clean_glucose_reading(self):
            someValue = self.cleaned_data['glucose_reading']


            if someValue[0] > 400 :
                raise forms.ValidationError('Value is too high.')
            elif someValue[0] < 0 :
                raise forms.ValidationError('Value must be more than zero.')
             
            if someValue[1] == 'mmo/L' and someValue[0] > 15:
                raise forms.ValidationError('Value is too high.')
            elif someValue[1] == 'mmo/L' and someValue[0] < 0:
                raise forms.ValidationError('Value must be more than zero.')

            if someValue[1] == 'mmo/L':
                someValue = someValue[0] * 18
            else:
                someValue = someValue[0]
            
            return someValue

class CarbReadingForm(forms.ModelForm):

    carb_reading = forms.IntegerField(required=True, widget= forms.NumberInput(attrs={'class':'form-control', 'placeholder':'Carbs Value    -g'}))
    record_datetime = forms.DateTimeField(required=True, widget = forms.DateTimeInput(attrs={'class':'form-control', 'placeholder':'DateTime'}),input_formats= '%Y-%m-%d %H:%M')
    

    class Meta():
               
        model = Carbohydrate
        fields = ('carb_reading','record_datetime')


    def clean_carb_reading(self):
            carbValue = self.cleaned_data['carb_reading']

            if carbValue > 300 :
                raise forms.ValidationError('Value is too high.')
            elif carbValue < 0 :
                raise forms.ValidationError('Value must be more than zero.')
class InsulinReadingForm(forms.ModelForm):
    
    dosage =forms.FloatField(required=True, widget= forms.NumberInput(attrs={'class':'form-control', 'placeholder':'Insulin unit'}))
    record_datetime = forms.DateTimeField(required=True, widget = forms.DateTimeInput(attrs={'class':'form-control', 'placeholder':'DateTime'}),input_formats= '%Y-%m-%d %H:%M')
    
    class Meta():
               
        model = Insulin
        fields = ('dosage','record_datetime')

    def clean_dosage(self):
            insulinDosage = self.cleaned_data['dosage']

            if insulinDosage > 50 :
                raise forms.ValidationError('Value is too high.')
            elif insulinDosage < 0 :
                raise forms.ValidationError('Value must be more than zero.')


class UpdateProfile(forms.ModelForm):

    class Meta():
        
        model = User
        fields = (
            'username',
            'email')
            

