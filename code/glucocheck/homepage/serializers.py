from rest_framework.serializers import ModelSerializer
from homepage.models import UserProfile, Glucose, Carbohydrate, Insulin, RecordingCategory
from rest_framework import serializers
from django.contrib.auth.models import User



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        '''Meta data on the form.
        
        Instance variables:
        model -- the model the form relates to
        fields -- the model fields the form fields relate to
        '''
        model = User
        fields = ('pk', 'email', 'first_name', 'last_name')


def validateGlucose(glucose_reading):
    ''' Validating glucose reading value entered by the user and return the validated value'''
            
    if  glucose_reading not in range(0,400):
        raise serializers.ValidationError('Glucose value should be between 0 and 400')
            
    return glucose_reading

class GlucoseSerializer(ModelSerializer):
    '''   
    Serializer class convert the model instances into native Python datatypes

    Instance variables:
    glucose_reading -- a glucose_reading field for the user to input the glucose recorded value with the validation 
    record_datetime -- a record_datetime field for the user to record the date time of glucose value
    user -- read the user serializer
    '''
    glucose_reading = serializers.IntegerField(validators=[validateGlucose],help_text='Integer value in mg/dl unit.Glucose value should be between 0 and 400') 
    record_datetime = serializers.DateTimeField(help_text='Date Time field in the format Y-M-D H:M:S')
    user = UserSerializer(required=False, read_only=True)
    class Meta:
        '''Meta data on the form.
        
        Instance variables:
        model -- the model the form relates to
        fields -- the model fields the form fields relate to
        '''
        model = Glucose
        fields = ['id','user','glucose_reading','record_datetime','notes','categories']

    

def validateCarb(carb_reading):
    ''' Validating carb reading value entered by the user and return the validated value'''
    
    if carb_reading not in range(0,300) :
        raise serializers.ValidationError('Carbs value should be between 0 and 300')
    
    return carb_reading   

class CarbohydrateSerializer(ModelSerializer):
    '''   
    Serializer class convert the model instances into native Python datatypes

    Instance variables:
    carb_reading -- a carb_reading field for the user to input the carbohydrate recorded value with the validation 
    record_datetime -- a record_datetime field for the user to record the date time 
    user -- read the user serializer
    '''
    carb_reading = serializers.IntegerField(validators=[validateCarb],help_text='Integer value of carbohydrate between 0 and 300.') 
    record_datetime = serializers.DateTimeField(help_text='Date Time field in the format Y-M-D H:M:S')
    user = UserSerializer(required=False, read_only=True)
    class Meta:
        '''Meta data on the form.
        
        Instance variables:
        model -- the model the form relates to
        fields -- the model fields the form fields relate to
        '''
        model = Carbohydrate
        fields = ['id','user','carb_reading','record_datetime']

    
def validateDosage(dosage):
    ''' Validating insulin dosage value entered by the user and return the validated value'''
    
    if dosage not in range(0,50) :
        raise serializers.ValidationError('Insulin value should be between 0 and 50')
    
    return dosage

class InsulinSerializer(ModelSerializer):
    '''   
    Serializer class convert the model instances into native Python datatypes

    Instance variables:
    dosage -- a insulin dosage field for the user to input the insulin recorded value with the validation 
    record_datetime -- a record_datetime field for the user to record the date time 
    user -- read the user serializer
    '''
    dosage = serializers.FloatField(validators=[validateDosage],help_text='Float value of insulin between 0 and 50')
    record_datetime = serializers.DateTimeField(help_text='Date Time field in the format Y-M-D H:M:S')
    user = UserSerializer(required=False, read_only=True) 
    class Meta:
        '''Meta data on the form.
        
        Instance variables:
        model -- the model the form relates to
        fields -- the model fields the form fields relate to
        '''
        model = Insulin
        fields = ['id','user','dosage','record_datetime']