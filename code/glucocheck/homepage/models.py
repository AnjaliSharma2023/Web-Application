from django.db import models
from django.contrib.auth.models import User

# Create your models here.



class Country(models.Model):

    state = models.CharField(max_length= 40)


    def __str__(self):
        return self.state


class UserProfile(models.Model):
    user = models.OneToOneField(User,on_delete= models.CASCADE)
    email = models.CharField(max_length=200)
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    birth_date = models.DateField(default=None)
    state = models.CharField(max_length=200)

    def __str__(self):
        return self.user.username