from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class SignupForm(UserCreationForm):
    username = forms.CharField(required =True)
    email=forms.EmailField(required =True)
    birth_date = forms.DateField(label ='Date of birth',widget = forms.SelectDateWidget)
    state = forms.CharField(max_length = 20,required =True)
   

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


    '''def save(self, commit =True):
        user = super(SignupForm,self).save(commit= False)
        

        if commit: 
            user.save()

        #return user
    '''
