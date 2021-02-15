from django.db import models
from django.contrib.auth.models import User

# Create your models here.



class Country(models.Model):

    name = models.CharField(max_length=40)

    def __str__(self):
        return self.name

class State(models.Model):

    country = models.ForeignKey(Country, on_delete = models.CASCADE)
    name = models.CharField(max_length= 40)

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    user = models.OneToOneField(User,on_delete= models.CASCADE)
    email = models.CharField(max_length=200,null =True)
    first_name = models.CharField(max_length=200, null=True)
    last_name = models.CharField(max_length=200, null=True)
    country = models.ForeignKey(Country, on_delete= models.SET_NULL, null = True )
    state = models.ForeignKey(State, on_delete= models.SET_NULL, null = True)


    def __str__(self):
        return self.user.username