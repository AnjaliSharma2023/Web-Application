from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.contrib.auth.models import User
from homepage.models import UserProfile, RecordingCategory, Glucose, Carbohydrate, Insulin
from datetime import datetime, date, timedelta
import pandas as pd
from random import randint
from pytz import UTC


class SetupVisualizationDatasets(StaticLiveServerTestCase):
    @staticmethod
    def setUpTestData(num_users):
        def _createUser(user_num, behavior_score, num_days):
            # Glucose and carbohydrate are subjective mg/dL & carb ranges
            # Insulin is the relative minutes for when the dosage was given compared to the carbohydrates
            # Insulin and carbohydrates have a repeated awful range for consistancy
            ranges = { 'glucose': { 'perfect': [100, 120], 'good': [65, 160], 'bad': [50, 300], 'awful': [40, 400]},
                       'carbohydrate': { 'perfect': [20, 40], 'good': [30, 80], 'bad': [60, 150], 'awful': [60, 150]},
                       'insulin': { 'perfect': [-20, -10], 'good': [-10, 10], 'bad': [5, 15], 'awful': [5,15]}}
        
            birth_date = datetime.today().replace(year=datetime.today().year - 19)
            
            new_user = User.objects.create_user(username=f'test_user{user_num}', password=f'testPassword{user_num}', email=f'testEmail{user_num}@gmail.com')
            new_user_profile = UserProfile.objects.create(user=new_user, birth_date=birth_date, state='Arizona')
            
            start_date = date.today() - timedelta(days=num_days)
            
            range_roll_value = randint(behavior_score,100)
            if range_roll_value >= 90:
                new_user_range = 'perfect'
            elif range_roll_value >= 50:
                new_user_range = 'good'
            elif range_roll_value >= 10:
                new_user_range = 'bad'
            else:
                new_user_range = 'awful'
            
            for day in pd.date_range(start=start_date,end=date.today()).to_pydatetime():
                # Glucose
                # Breakfast
                if behavior_score >= randint(0, 100):
                    time = day.replace(hour=randint(6,8), minute=randint(0,59), second=randint(0,59))
                    glucose_value = randint(ranges['glucose'][new_user_range][0], ranges['glucose'][new_user_range][1])
                    category = RecordingCategory.objects.get(pk=randint(1,3))
                    breakfast_reading = Glucose.objects.create(user=new_user, glucose_reading=glucose_value, record_datetime=time, notes="")
                    breakfast_reading.categories.add(category)
                    breakfast_reading.save()
                else:
                    breakfast_reading = None
                

                # Snack 1
                if behavior_score < randint(0,100):
                    # Increase range due to insulin activation rate if breakfast time was on the later margin
                    if breakfast_reading is None:
                        lower_range = ranges['glucose'][new_user_range][0]
                        upper_range = ranges['glucose'][new_user_range][1]
                    else:
                        hours = randint(0,1)
                        minutes = randint(0,59)
                        seconds = randint(0,59)
                        
                        time = breakfast_reading.record_datetime + timedelta(hours=hours, minutes=minutes, seconds=seconds)
                        
                        seconds_elapsed = (time - breakfast_reading.record_datetime).total_seconds()
                        if seconds_elapsed >= 5400:
                            if new_user_range in ['perfect', 'good']:
                                lower_range = ranges['glucose'][new_user_range][0] + 40
                                upper_range = ranges['glucose'][new_user_range][1] + 40
                            else:
                                lower_range = ranges['glucose'][new_user_range][0] + 100
                                upper_range = ranges['glucose'][new_user_range][1]
                        else:
                            lower_range = ranges['glucose'][new_user_range][0]
                            upper_range = ranges['glucose'][new_user_range][1]
                        
                        
                        
                    
                    glucose_value = randint(lower_range, upper_range)
                
                # Lunch
                if behavior_score >= randint(0, 100):
                    time = day.replace(hour=randint(11,13), minute=randint(0,59), second=randint(0,59))
                    glucose_value = randint(ranges['glucose'][new_user_range][0], ranges['glucose'][new_user_range][1])
                    category = randint(1,3)
                    # Fasting
                    if category == 1:
                        category = RecordingCategory.objects.get(pk=1)
                    # Before/After Lunch
                    else:
                        category += 2
                        category = RecordingCategory.objects.get(pk=category)
                else:
                    lunch_reading = None
                    
                # Dinner    
                if behavior_score >= randint(0, 100):
                    time = day.replace(hour=randint(17,20), minute=randint(0,59), second=randint(0,59))
                    glucose_value = randint(ranges['glucose'][new_user_range][0], ranges['glucose'][new_user_range][1])
                    category = randint(1,3)
                    # Fasting
                    if category == 1:
                        category = RecordingCategory.objects.get(pk=1)
                    # Before/After Dinner
                    else:
                        category += 5
                        category = RecordingCategory.objects.get(pk=category)
                else:
                    dinner_reading = None
                
                # Bedtime
                if behavior_score >= randint(0, 100):
                    hour = randint(21,25)
                    if hour >= 24:
                        hour -= 24
                        bedtime_day = day + timedelta(days=1)
                        time = bedtime_day.replace(hour=hour, minute=randint(0,59), second=randint(0,59))
                    else:
                        time = day.replace(hour=hour, minute=randint(0,59), second=randint(0,59))
                    
                    glucose_value = randint(ranges['glucose'][new_user_range][0], ranges['glucose'][new_user_range][1])
                    category = randint(1,3)
                    # Fasting
                    if category == 1:
                        category = RecordingCategory.objects.get(pk=1)
                    # Snacks
                    elif category == 2:
                        category += 4
                        category = RecordingCategory.objects.get(pk=category)
                    # After Dinner
                    else:
                        category += 5
                        category = RecordingCategory.objects.get(pk=category)
                else:
                    bedtime_reading = None
                        
                    
                # Carbohydrate
                if behavior_score >= randint(0, 100):
                    pass
                
                # Insulin
                if behavior_score >= randint(0, 100):
                    pass
        
        recording_categories = ['fasting', 'before breakfast', 'after breakfast', 'before lunch', 'after lunch', 'snacks', 'before dinner', 'after dinner']
        index = 0
        for category in recording_categories:
            recording_categories[index] = RecordingCategory.objects.create(name=category)
        
        _createUser(1, 50, 30)
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.setUpTestData(1)
        print(User.objects.all())
        print(UserProfile.objects.all())
        for object in RecordingCategory.objects.all():
            print(object.pk)
        
        