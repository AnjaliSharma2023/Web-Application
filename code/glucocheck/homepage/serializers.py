from rest_framework.serializers import ModelSerializer
from homepage.models import UserProfile, Glucose, Carbohydrate, Insulin, RecordingCategory
from rest_framework import serializers
from django.contrib.auth.models import User
from homepage.fields import FloatWithUnitField, IntWithUnitField
from homepage.widgets import CheckboxLink, InputWithSelector


def validateGlucose(glucose_reading):
            
            if  glucose_reading not in range(0,400):
                raise serializers.ValidationError('Glucose value should be between 0 and 400')
                   
            return glucose_reading

class GlucoseSerializer(ModelSerializer):
    glucose_reading = serializers.IntegerField(validators=[validateGlucose]) 

    class Meta:
        model = Glucose
        fields = ['id','glucose_reading','record_datetime','notes','categories']

    

def validateCarb(carb_reading):

    if carb_reading not in range(0,300) :
        raise serializers.ValidationError('Carbs value should be between 0 and 300')
    
    return carb_reading   

class CarbohydrateSerializer(ModelSerializer):
    carb_reading = serializers.IntegerField(validators=[validateCarb]) 
    class Meta:
        model = Carbohydrate
        fields = ['id','carb_reading','record_datetime']

    
def validateDosage(dosage):
 
        if dosage not in range(0,50) :
            raise serializers.ValidationError('Insulin value should be between 0 and 50')
        
        return dosage


class InsulinSerializer(ModelSerializer):
    dosage = serializers.IntegerField(validators=[validateDosage]) 
    class Meta:
        model = Insulin
        fields = ['id','dosage','record_datetime']