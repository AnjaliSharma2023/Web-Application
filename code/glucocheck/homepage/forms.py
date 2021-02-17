from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile

class SignupForm(UserCreationForm):
    username = forms.CharField(required =True, widget=forms.TextInput(attrs={'placeholder':'Username'}), label='username.svg')
    email=forms.EmailField(required =True, widget=forms.TextInput(attrs={'placeholder':'Email'}), label='username.svg')
    birth_date = forms.DateField(widget = forms.SelectDateWidget(attrs={'placeholder':'Birth Date'}), label='username.svg')
    state = forms.CharField(max_length = 20,required =True, widget=forms.TextInput(attrs={'placeholder':'State'}), label='username.svg')
    password1 = forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder':'Password'}), label='username.svg')
    password2 = forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder':'Password Confirmation'}), label='username.svg')
    '''
    email=forms.EmailField(required =True)
    birth_date = forms.DateField(label ='Date of birth',help_text='Required. Format: MM-DD-YYYY')
    state = forms.CharField(max_length = 20)
    '''
    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'password1',
            'password2',
            'birth_date',
            'state',
        ) 

    def save(self, commit =True):
        user = super().save(commit= False)
        
        user.email = self.cleaned_data['email']
        user.birth_date = self.cleaned_data['birth_date']
        user.state = self.cleaned_data['state']

        if commit: 
            user.save()

        return user


class UserProfileForm(forms.ModelForm):
    class Meta():
        model = UserProfile
        fields = ('birth_date','state')

