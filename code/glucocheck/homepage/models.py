from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

# Create your models here.

class UserProfile(models.Model):  
    user = models.OneToOneField(User,on_delete= models.CASCADE)# relationship of user attribute with User model 
    # every profile associated with one user and every user will have one profile                      
    birth_date = models.DateField(null=True, blank=True)
    state = models.CharField(max_length=200)
    


    def __str__(self):
        return self.user.username

# This signal creates Auth Token for new users
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)

class RecordingCategory(models.Model):
    categories_choices =[
        ('fasting','Fasting'),
        ('before breakfast','Before Breakfast'),
        ('after breakfast','After Breakfast'),
        ('before lunch','Before Lunch'),
        ('after lunch','After Lunch'),
        ('snacks','Snacks'),
        ('before dinner','Before Dinner'),
        ('after dinner','After Dinner'),
    ]

    name = models.CharField(choices = categories_choices,unique=True,max_length=255)
    
    def __str__(self):
        return self.name

class Glucose(models.Model):
    user = models.ForeignKey(User, on_delete= models.DO_NOTHING)
    glucose_reading = models.PositiveIntegerField()
    record_datetime = models.DateTimeField()
    #record_time = models.TimeField()
    notes = models.TextField(blank=True)
    categories = models.ForeignKey(RecordingCategory, on_delete= models.DO_NOTHING, null=False)


    def __str__(self):
        return str(self.glucose_reading)

class Carbohydrate(models.Model):
    user = models.ForeignKey(User, on_delete= models.DO_NOTHING)
    carb_reading = models.PositiveIntegerField()
    record_datetime = models.DateTimeField()


    def __str__(self):
        return str(self.carb_reading)

class Insulin(models.Model):

    user = models.ForeignKey(User, on_delete= models.DO_NOTHING)
    dosage = models.FloatField()
    record_datetime = models.DateTimeField()
    
    def __str__(self):
        return str(self.dosage)
  