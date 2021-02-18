from django.db import models
from django.contrib.auth.models import User

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
                              
    birth_date = models.DateField(null=True,blank=True)
    state = models.CharField(max_length=200)

    def __str__(self):
        return self.user.username