from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class UserProfile(models.Model):
    user = models.OneToOneField(User,on_delete= models.CASCADE)
    
    birth_date = models.DateField(null=True,blank=True)
    state = models.CharField(max_length=200)

    def __str__(self):
        return self.user.username