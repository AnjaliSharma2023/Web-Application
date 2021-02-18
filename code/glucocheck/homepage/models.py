from django.db import models
from django.contrib.auth.models import User
    
from localflavor.us.forms import USStateSelect
from datetime import date


# Create your models here.

class UserProfile(models.Model):
    user = models.OneToOneField(User,on_delete= models.CASCADE)# relationship of user attribute with User model 
    # every profile associated with one user and every user will have one profile
    
    '''Male = 'M'
    FeMale = 'F'
    GENDER_CHOICES = (
    (Male, 'Male'),
    (FeMale, 'Female'),
    ) 
    gender = models.CharField(max_length = 6, choices = GENDER_CHOICES) 
    '''
                              
    birth_date = models.DateField()
    state = models.CharField(max_length=200)

    '''def set_adult(self):
        today = date.today()
        age = today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
        if age > 18:
            self.adult = True
        else:
            self.adult = False
    '''

    def clean_date_of_birth(self):
        birth_date = self.cleaned_data['birth_date']
        today = date.today()
        if (birth_date.year + 18, birth_date.month, birth_date.day) > (today.year, today.month, today.day):
            raise forms.ValidationError('Must be at least 18 years old to register')
        return birth_date

    def __str__(self):
        return self.user.username