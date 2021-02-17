from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile

class SignupForm(UserCreationForm):
    username = forms.CharField(required =True)
    email=forms.EmailField(required =True)
    birth_date = forms.DateField(label ='Date of birth',widget = forms.SelectDateWidget(years=range(1910, 2003)))
    state = forms.CharField(max_length = 20)
   

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


'''class InfoProfile(forms.ModelForm):
    class Meta():
        model = UserProfile
        fields =('birth_date','state')





    def save(self, commit =True):
        user = super(SignupForm,self).save(commit= False)
        

        if commit: 
            user.save()

        #return user
    '''
