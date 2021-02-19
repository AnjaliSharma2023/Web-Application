from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile
from datetime import date
from .widgets import CheckboxLink
from localflavor.us.forms import USStateSelect


class SignupForm(UserCreationForm):
    username = forms.CharField(required =True, widget=forms.TextInput(attrs={'placeholder':'Username'}), label='user.svg')
    email=forms.EmailField(required =True, widget=forms.TextInput(attrs={'placeholder':'Email'}), label='envelope.svg')
    password1 = forms.CharField(required=True, widget=forms.PasswordInput(attrs={'placeholder':'Password'}), label='key.svg')
    password2 = forms.CharField(required=True, widget=forms.PasswordInput(attrs={'placeholder':'Password Confirmation'}), label='key.svg')
    
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


class UserProfileForm(forms.ModelForm): #
    birth_date = forms.DateField(widget = forms.DateInput(attrs={'placeholder':'Birth Date', 'onfocus':"(this.type='date')", 'onfocusout':"(this.type='text')"}), label='calendar-alt.svg')
    state = forms.CharField(required =True, widget=USStateSelect(attrs={'placeholder':'State'}), label='map-marker-alt.svg')
    signup_confirmation = forms.BooleanField(required =True, widget=CheckboxLink(link_text='TNC', side_text='Have you have read and agree to the ', wrap_elem='div', wrap_elem_attrs={'class':'column'}, link_attrs={'href':"{% url 'login' %}"}), label="user.svg")
    
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
    username = forms.CharField(required =True, widget=forms.TextInput(attrs={'placeholder':'Username'}), label='user.svg')
    password = forms.CharField(required=True, widget=forms.PasswordInput(attrs={'placeholder':'Password'}), label='key.svg')

