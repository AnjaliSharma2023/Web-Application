from rest_framework.serializers import ModelSerializer
from homepage.models import UserProfile, Glucose, Carbohydrate, Insulin, RecordingCategory
from rest_framework import serializers
from django.contrib.auth.models import User

class GlucoseSerializer(ModelSerializer):
    
    class Meta:
        model = Glucose
        fields = '__all__'
