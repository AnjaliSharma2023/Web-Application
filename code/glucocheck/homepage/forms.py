from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile
#from django.contrib.localflavor.us.us_states import STATE_CHOICES

    
from localflavor.us.forms import USStateSelect

# from django.contrib.localflavor.us.models import USStateField
class SignupForm(UserCreationForm):
    username = forms.CharField(required =True, widget=forms.TextInput(attrs={'placeholder':'Username'}), label='user.svg')
    email=forms.EmailField(required =True, widget=forms.TextInput(attrs={'placeholder':'Email'}), label='envelope.svg')
    birth_date = forms.DateField(widget = forms.SelectDateWidget(attrs={'placeholder':'Birth Date'}), label='calendar-alt.svg')
    #state = USStateField(choices = STATE_CHOICES)
    state = forms.CharField(required =True, widget=USStateSelect(attrs={'placeholder':'State'}), label='map-marker-alt.svg')
    #state = USStateSelect(required =True, widget=forms.TextInput(attrs={'placeholder':'State'}), label='map-marker-alt.svg')
    password1 = forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder':'Password'}), label='key.svg')
    password2 = forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder':'Password Confirmation'}), label='key.svg')
    '''
    email=forms.EmailField(required =True)
    birth_date = forms.DateField(input_formats=['%d/%m/%Y'])
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


class UserProfileForm(forms.ModelForm): #
    class Meta():
        model = UserProfile
        fields = ('birth_date','state')

