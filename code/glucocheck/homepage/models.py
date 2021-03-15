from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class UserProfile(models.Model):  
    user = models.OneToOneField(User,on_delete= models.CASCADE)# relationship of user attribute with User model 
    # every profile associated with one user and every user will have one profile                      
    birth_date = models.DateField(null=True, blank=True)
    state = models.CharField(max_length=200)
    #unit = models.CharField(max_length = 20)


    def __str__(self):
        return self.user.username


'''class Unit(models.Model):

    unit_category = models.CharField(unique=True, max_length=20)
    unit_name = models.CharField(unique=True, max_length=20)

    def __str__(self):
        return self.unit_name
'''

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
    notes = models.TextField()
    categories = models.ManyToManyField(RecordingCategory)

    #units = models.ForeignKey(Unit, on_delete= models.DO_NOTHING)

    def __str__(self):
        return self.glucose_reading

class Carbohydrate(models.Model):
    user = models.ForeignKey(User, on_delete= models.DO_NOTHING)
    carb_reading = models.PositiveIntegerField()
    record_datetime = models.DateTimeField()

    #units = models.ForeignKey(Unit, on_delete= models.DO_NOTHING)

    def __str__(self):
        return self.carb_reading

class Insulin(models.Model):

    user = models.ForeignKey(User, on_delete= models.DO_NOTHING)
    dosage =models.PositiveIntegerField()
    record_datetime = models.DateTimeField()
  
    #units = models.ForeignKey(Unit, on_delete= models.DO_NOTHING)