from django.db import models
from django.contrib.auth.models import User

from django.db.models.signals import post_save
from django.dispatch import receiver


# Create your models here.

class UserProfile(models.Model):  
    user = models.OneToOneField(User,on_delete= models.CASCADE)# relationship of user attribute with User model 
    # every profile associated with one user and every user will have one profile                      
    birth_date = models.DateField(null=True, blank=True)
    state = models.CharField(max_length=200)


    def __str__(self):
        return self.user.username



'''
@receiver(post_save, sender=User)
def user_to_inactive(sender, instance, created, update_fields, **kwargs):
    if created:
        instance.is_active = False
'''