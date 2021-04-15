from rest_framework.serializers import ModelSerializer
from homepage.models import UserProfile, Glucose, Carbohydrate, Insulin, RecordingCategory
from rest_framework import serializers
from django.contrib.auth.models import User



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('pk', 'email', 'first_name', 'last_name')


def validateGlucose(glucose_reading):
            
            if  glucose_reading not in range(0,400):
                raise serializers.ValidationError('Glucose value should be between 0 and 400')
                   
            return glucose_reading

class GlucoseSerializer(ModelSerializer):
    glucose_reading = serializers.IntegerField(validators=[validateGlucose],help_text='Integer value in mg/dl unit.Glucose value should be between 0 and 400') 
    record_datetime = serializers.DateTimeField(help_text='Date Time field in the format Y-M-D H:S:M')
    user = UserSerializer(required=False, read_only=True)
    class Meta:
        model = Glucose
        fields = ['id','user','glucose_reading','record_datetime','notes','categories']

    

def validateCarb(carb_reading):

    if carb_reading not in range(0,300) :
        raise serializers.ValidationError('Carbs value should be between 0 and 300')
    
    return carb_reading   

class CarbohydrateSerializer(ModelSerializer):
    carb_reading = serializers.IntegerField(validators=[validateCarb],help_text='Integer value of carbohydrate between 0 and 300.') 
    record_datetime = serializers.DateTimeField(help_text='Date Time field in the format Y-M-D H:S:M')
    user = UserSerializer(required=False, read_only=True)
    class Meta:
        model = Carbohydrate
        fields = ['id','user','carb_reading','record_datetime']

    
def validateDosage(dosage):
 
        if dosage not in range(0,50) :
            raise serializers.ValidationError('Insulin value should be between 0 and 50')
        
        return dosage


class InsulinSerializer(ModelSerializer):
    dosage = serializers.FloatField(validators=[validateDosage],help_text='Float value of insulin between 0 and 50')
    record_datetime = serializers.DateTimeField(help_text='Date Time field in the format Y-M-D H:S:M')
    user = UserSerializer(required=False, read_only=True) 
    class Meta:
        model = Insulin
        fields = ['id','user','dosage','record_datetime']