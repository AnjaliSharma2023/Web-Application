from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile
from datetime import date
from .widgets import CheckboxLink
from localflavor.us.forms import USStateSelect
from django.contrib.auth import authenticate


class SignupForm(UserCreationForm):
    username = forms.CharField(required =True, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Username'}), label='user.svg')
    email=forms.EmailField(required =True, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Email'}), label='envelope.svg')
    password1 = forms.CharField(required=True, widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'Password'}), label='key.svg')
    password2 = forms.CharField(required=True, widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'Password Confirmation'}), label='key.svg')
    
    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'password1',
            'password2',
        ) 

    

    def save(self, commit =True):
        user = super().save(commit= False)
        
        user.email = self.cleaned_data['email']
        
        #user.birth_date = self.cleaned_data['birth_date']
        
        

        if commit: 
            user.save()

        return user

# new form for the profile
class UserProfileForm(forms.ModelForm): #
    birth_date = forms.DateField(required=True,widget = forms.DateInput(attrs={'class':'form-control', 'placeholder':'Birth Date', 'onfocus':"(this.type='date')", 'onfocusout':"(this.type='text')"}), label='calendar-alt.svg')
    state = forms.CharField(required =True, widget=USStateSelect(attrs={'class':'form-control', 'placeholder':'State'}), label='map-marker-alt.svg')

    signup_confirmation = forms.BooleanField(required =True, widget=CheckboxLink(link_text='TNC', side_text='Have you have read and agree to the ', wrap_elem='div', wrap_elem_attrs={'class':'column'}, link_attrs={'target':'_blank', 'rel':'noreferrer noopener', 'href':"../tnc/"}), label="user.svg")
    

    class Meta():
        model = UserProfile
        fields = ('birth_date','state')
        
    def clean_birth_date(self):

        birth_date = self.cleaned_data['birth_date']
        today = date.today()
        if (birth_date.year + 18, birth_date.month, birth_date.day) > (today.year, today.month, today.day):
            raise forms.ValidationError('Must be at least 18 years old to register')
        return birth_date
        
class LoginForm(forms.Form):
    username = forms.CharField(required =True, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Username'}), label='user.svg')
    password = forms.CharField(required=True, widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'Password'}), label='key.svg')
    remember_me = forms.BooleanField(required =False, widget=CheckboxLink(side_text='Remember me', wrap_elem='div', wrap_elem_attrs={'class':'column'}), label="user.svg")
    
    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        password = cleaned_data.get("password")
        
        user = authenticate(username = username, password = password)
        if user is not None:
            if user.is_active == False:
                raise forms.ValidationError('Your account is not authenticated, please click the link in your email')
        else:
            raise forms.ValidationError('Your username OR password is incorrect')
            
class ResetPassword(forms.Form):
    password1 = forms.CharField(required=True, widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'New Password'}), label='key.svg')
    password2 = forms.CharField(required=True, widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'Password Confirmation'}), label='key.svg')
    
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
    
        if password1 != password2:
            raise forms.ValidationError('Your passwords do not match, please try again')
            
class ResetPasswordEmail(forms.Form):
    email = forms.EmailField(required =True, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Email'}), label='envelope.svg')
    
    def clean_email(self):
        email = self.cleaned_data['email']
        
        try:
            User.objects.get(email=email)
        except User.DoesNotExist:
            raise forms.ValidationError('This email is not associated with a user')
            
        return email
    

