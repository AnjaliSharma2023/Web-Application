from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class SignupForm(UserCreationForm):
    username = forms.CharField(required =True)
    email=forms.EmailField(required =True)
    state = forms.CharField(max_length = 20,required =True)
    country = forms.CharField(max_length = 20,required =True)

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'password1',
            'password2',
            'state',
            'country',
        ) 


    '''def save(self, commit =True):
        user = super(SignupForm,self).save(commit= False)
        

        if commit: 
            user.save()

        #return user
    '''
