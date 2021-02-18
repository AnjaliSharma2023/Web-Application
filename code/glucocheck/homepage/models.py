from django.db import models
from django.contrib.auth.models import User
    
from localflavor.us.forms import USStateSelect
from datetime import date


# Create your models here.

class UserProfile(models.Model):
    user = models.OneToOneField(User,on_delete= models.CASCADE)# relationship of user attribute with User model 
    # every profile associated with one user and every user will have one profile
                                 
    birth_date = models.DateField()
    state = models.CharField(max_length=200)

    
    def __str__(self):
        return self.user.username