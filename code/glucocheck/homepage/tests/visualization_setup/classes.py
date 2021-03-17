from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.contrib.auth.models import User
from homepage.models import UserProfile, RecordingCategory, Glucose, Carbohydrate, Insulin
from datetime import datetime, date, timedelta
import pandas as pd
from random import randint
from math import ceil


class SetupVisualizationDatasets(StaticLiveServerTestCase):
    @staticmethod
    def setUpTestData(num_users):
        def _getCategory(mealtime, behavior_score):
            category = randint(0, 100)
            if mealtime in ['snack1', 'snack2']:
                category = 6
            elif mealtime == 'breakfast':
                if behavior_score + 35 < category:
                    category = 1
                elif behavior_score < category:
                    category = 2
                else:
                    category = 3
                    
            elif mealtime in ['lunch', 'dinner']:
                if behavior_score + 50 < category:
                    category = 1
                elif behavior_score < category:
                    category = 2
                else:
                    category = 3
                    
            else:
                if behavior_score < category:
                    category = 1
                else:
                    category = 6
            
            if mealtime == 'lunch':
                if category != 1:
                    category += 2
            elif mealtime == 'dinner':
                if category != 1:
                    category += 5
            
            return RecordingCategory.objects.get(pk=category)
            
        def _glucoseRangesAndTime(prev_reading, user_range, day, hour_range):
            if prev_reading is None:
                lower_range = ranges['glucose'][user_range][0]
                upper_range = ranges['glucose'][user_range][1]
                
                hour = randint(hour_range[0], hour_range[1])
                if hour >= 24:
                    hour -= 24
                    new_day = day + timedelta(days=1)
                    time = new_day.replace(hour=hour, minute=randint(0,59), second=randint(0,59))
                else:
                    time = day.replace(hour=hour, minute=randint(0,59), second=randint(0,59))
            
            else:
                hour = randint(hour_range[0], hour_range[1])
                if hour >= 24:
                    hour -= 24
                    new_day = day + timedelta(days=1)
                    time = new_day.replace(hour=hour, minute=randint(0,59), second=randint(0,59))
                else:
                    time = day.replace(hour=hour, minute=randint(0,59), second=randint(0,59))
                
                seconds_elapsed = (time - prev_reading.record_datetime).total_seconds()
                if seconds_elapsed >= 5400:
                    if user_range in ['perfect', 'good']:
                        lower_range = ranges['glucose'][user_range][0] + 40
                        upper_range = ranges['glucose'][user_range][1] + 40
                    else:
                        lower_range = ranges['glucose'][user_range][0] + 100
                        upper_range = ranges['glucose'][user_range][1]
                else:
                    lower_range = ranges['glucose'][user_range][0]
                    upper_range = ranges['glucose'][user_range][1]
                    
            return time, lower_range, upper_range
            
        def _carbRangesAndTime(glucose_reading, user_range, day, hour_range, behavior_score):
            if glucose_reading is None:
                hour = randint(hour_range[0], hour_range[1])
                if hour >= 24:
                    hour -= 24
                    new_day = day + timedelta(days=1)
                    time = new_day.replace(hour=hour, minute=randint(0,59), second=randint(0,59))
                else:
                    time = day.replace(hour=hour, minute=randint(0,59), second=randint(0,59))
                    
            else:
                if behavior_score == 100:
                    inverse_behavior_score = 1 - 99/100
                else:
                    inverse_behavior_score = 1 - behavior_score/100
                
                if 'before' in glucose_reading.categories.name:
                    time = glucose_reading.record_datetime + timedelta(minutes=ceil(randint(10,15) * inverse_behavior_score), seconds=randint(0,59))
                elif 'after' in glucose_reading.categories.name:
                    time = glucose_reading.record_datetime - timedelta(minutes=ceil(randint(10,15) * inverse_behavior_score), seconds=randint(0,59))
                else:
                    if randint(behavior_score, 100) >= 75: 
                        time = glucose_reading.record_datetime - timedelta(minutes=ceil(randint(10,15) * inverse_behavior_score), seconds=randint(0,59))
                    else:
                        time = glucose_reading.record_datetime + timedelta(minutes=ceil(randint(10,15) * inverse_behavior_score), seconds=randint(0,59))
                
            lower_range = ranges['carbohydrate'][user_range][0]
            upper_range = ranges['carbohydrate'][user_range][1]
            
            return time, lower_range, upper_range
            
        def _dosageTime(glucose_reading, carb_reading, user_range, behavior_score):
            if glucose_reading is not None:
                time = glucose_reading.record_datetime + timedelta(minutes=ceil(randint(0,5) * behavior_score/100), seconds=randint(0,59))
            else:
                minute_value = randint(ranges['insulin'][user_range][0], ranges['insulin'][user_range][1])
                if minute_value < 0:
                    time = carb_reading.record_datetime - timedelta(minutes=abs(minute_value))
                else:
                    time = carb_reading.record_datetime + timedelta(minutes=minute_value)
                    
            return time
                
        def _createUser(user_num, behavior_score, new_user_range, num_days):
            birth_date = datetime.today().replace(year=datetime.today().year - 19)
            
            new_user = User.objects.create_user(username=f'test_user{user_num}', password=f'testPassword{user_num}', email=f'testEmail{user_num}@gmail.com')
            new_user_profile = UserProfile.objects.create(user=new_user, birth_date=birth_date, state='Arizona')
            
            start_date = date.today() - timedelta(days=num_days)
            
            for day in pd.date_range(start=start_date,end=date.today()).to_pydatetime():
                # Glucose
                # Breakfast
                if behavior_score >= randint(0, 100):
                    time, lower_range, upper_range = _glucoseRangesAndTime(None, new_user_range, day, mealtime_ranges['breakfast'])
                    glucose_value = randint(lower_range, upper_range)
                    category = _getCategory('breakfast', behavior_score)
                    
                    breakfast_reading = Glucose.objects.create(user=new_user, glucose_reading=glucose_value, record_datetime=time, categories=category, notes="")
                else:
                    breakfast_reading = None

                # Snack 1
                if behavior_score < randint(0,100):
                    time, lower_range, upper_range = _glucoseRangesAndTime(breakfast_reading, new_user_range, day, mealtime_ranges['snack1'])   
                    glucose_value = randint(lower_range, upper_range)
                    category = _getCategory('snack1', behavior_score)
                    
                    snack1_reading = Glucose.objects.create(user=new_user, glucose_reading=glucose_value, record_datetime=time, categories=category, notes="")
                else:
                    snack1_reading = None
                
                # Lunch
                if behavior_score >= randint(0, 100):
                    time, lower_range, upper_range = _glucoseRangesAndTime(snack1_reading, new_user_range, day, mealtime_ranges['lunch'])
                    glucose_value = randint(lower_range, upper_range)
                    category = _getCategory('lunch', behavior_score)
                        
                    lunch_reading = Glucose.objects.create(user=new_user, glucose_reading=glucose_value, record_datetime=time, categories=category, notes="")
                else:
                    lunch_reading = None
                    
                # Snack 2
                if behavior_score < randint(0,100):
                    time, lower_range, upper_range = _glucoseRangesAndTime(lunch_reading, new_user_range, day, mealtime_ranges['snack2'])
                    glucose_value = randint(lower_range, upper_range)
                    category = _getCategory('snack2', behavior_score)
                    
                    snack2_reading = Glucose.objects.create(user=new_user, glucose_reading=glucose_value, record_datetime=time, categories=category, notes="")
                else:
                    snack2_reading = None
                    
                # Dinner    
                if behavior_score >= randint(0, 100):
                    time, lower_range, upper_range = _glucoseRangesAndTime(lunch_reading, new_user_range, day, mealtime_ranges['dinner'])
                    glucose_value = randint(lower_range, upper_range)
                    category = _getCategory('dinner', behavior_score)
                        
                    dinner_reading = Glucose.objects.create(user=new_user, glucose_reading=glucose_value, record_datetime=time, categories=category, notes="")
                else:
                    dinner_reading = None
                
                # Bedtime
                if behavior_score >= randint(0, 100):
                    time, lower_range, upper_range = _glucoseRangesAndTime(dinner_reading, new_user_range, day, mealtime_ranges['bedtime'])
                    glucose_value = randint(lower_range, upper_range)
                    category = _getCategory('bedtime', behavior_score)
                        
                    bedtime_reading = Glucose.objects.create(user=new_user, glucose_reading=glucose_value, record_datetime=time, categories=category, notes="")
                else:
                    bedtime_reading = None
                        
                   
                # Carbohydrate
                # Breakfast - forced trigger based on behavior score value
                if randint(behavior_score, 100) >= 75:
                    if breakfast_reading is not None and breakfast_reading.categories == 'fasting':
                        breakfast_carb = None
                    else:
                        time, lower_range, upper_range = _carbRangesAndTime(breakfast_reading, new_user_range, day, mealtime_ranges['breakfast'], behavior_score)
                        carb_value = randint(lower_range, upper_range)
                        
                        breakfast_carb = Carbohydrate.objects.create(user=new_user, carb_reading=carb_value, record_datetime=time)
                else:
                    breakfast_carb = None
                    
                # Snack1 - comp means a higher behavior score makes it less likely unless they took a snack1 reading
                if behavior_score < randint(0,100) or snack1_reading is not None:
                    time, lower_range, upper_range = _carbRangesAndTime(snack1_reading, new_user_range, day, mealtime_ranges['snack1'], behavior_score)
                    carb_value = randint(lower_range, upper_range)
                    
                    snack1_carb = Carbohydrate.objects.create(user=new_user, carb_reading=carb_value, record_datetime=time)  
                    
                else:
                    snack1_carb = None
                    
                # Lunch - forced trigger based on behavior score value
                if randint(behavior_score, 100) >= 50:
                    if lunch_reading is not None and lunch_reading.categories == 'fasting':
                        lunch_carb = None
                    else:
                        time, lower_range, upper_range = _carbRangesAndTime(lunch_reading, new_user_range, day, mealtime_ranges['lunch'], behavior_score)
                        carb_value = randint(lower_range, upper_range)
                        
                        lunch_carb = Carbohydrate.objects.create(user=new_user, carb_reading=carb_value, record_datetime=time)
                        
                else:
                    lunch_carb = None
                    
                # Snack2 - comp means a higher behavior score makes it less likely unless they took a snack1 reading
                if behavior_score < randint(0,100) or snack2_reading is not None:
                    time, lower_range, upper_range = _carbRangesAndTime(snack2_reading, new_user_range, day, mealtime_ranges['snack2'], behavior_score)
                    carb_value = randint(lower_range, upper_range)
                    
                    snack2_carb = Carbohydrate.objects.create(user=new_user, carb_reading=carb_value, record_datetime=time)
                    
                else:
                    snack2_carb = None
                
                # Dinner - forced trigger based on behavior score value
                if randint(behavior_score, 100) >= 25:
                    if dinner_reading is not None and dinner_reading.categories == 'fasting':
                        dinner_carb = None
                    else:
                        time, lower_range, upper_range = _carbRangesAndTime(dinner_reading, new_user_range, day, mealtime_ranges['dinner'], behavior_score)
                        carb_value = randint(lower_range, upper_range)
                        
                        dinner_carb = Carbohydrate.objects.create(user=new_user, carb_reading=carb_value, record_datetime=time)
                        
                else:
                    dinner_carb = None
                
                # Bedtime - comp means a higher behavior score makes it less likely
                if behavior_score < randint(0,100):
                    if bedtime_reading is not None and bedtime_reading.categories == 'fasting':
                        bedtime_carb = None
                    else:
                        time, lower_range, upper_range = _carbRangesAndTime(bedtime_reading, new_user_range, day, mealtime_ranges['bedtime'], behavior_score)
                        carb_value = randint(lower_range, upper_range)
                        
                        bedtime_carb = Carbohydrate.objects.create(user=new_user, carb_reading=carb_value, record_datetime=time)
                        
                else:
                    bedtime_carb = None
                
                
                # Insulin
                # Breakfast
                if breakfast_carb is not None:
                    time = _dosageTime(breakfast_reading, breakfast_carb, new_user_range, behavior_score)
                    dosage = breakfast_carb.carb_reading / 8 # 1:8 insulin to carb ratio, arbitrary
                    
                    breakfast_insulin = Insulin.objects.create(user=new_user, dosage=dosage, record_datetime=time)
                    
                else:
                    breakfast_insulin = None
                    
                # Snack1
                if snack1_carb is not None:
                    time = _dosageTime(snack1_reading, snack1_carb, new_user_range, behavior_score)
                    dosage = snack1_carb.carb_reading / 8 # 1:8 insulin to carb ratio, arbitrary
                    
                    snack1_insulin = Insulin.objects.create(user=new_user, dosage=dosage, record_datetime=time)
                    
                else:
                    snack1_insulin = None
                    
                # Lunch
                if lunch_carb is not None:
                    time = _dosageTime(lunch_reading, lunch_carb, new_user_range, behavior_score)
                    dosage = lunch_carb.carb_reading / 8 # 1:8 insulin to carb ratio, arbitrary
                    
                    lunch_insulin = Insulin.objects.create(user=new_user, dosage=dosage, record_datetime=time)
                    
                else:
                    lunch_insulin = None
                    
                # Snack2
                if snack2_carb is not None:
                    time = _dosageTime(snack2_reading, snack2_carb, new_user_range, behavior_score)
                    dosage = snack2_carb.carb_reading / 8 # 1:8 insulin to carb ratio, arbitrary
                    
                    snack2_insulin = Insulin.objects.create(user=new_user, dosage=dosage, record_datetime=time)
                    
                else:
                    snack2_insulin = None
                
                # Dinner
                if dinner_carb is not None:
                    time = _dosageTime(dinner_reading, dinner_carb, new_user_range, behavior_score)
                    dosage = dinner_carb.carb_reading / 8 # 1:8 insulin to carb ratio, arbitrary
                    
                    dinner_insulin = Insulin.objects.create(user=new_user, dosage=dosage, record_datetime=time)
                    
                else:
                    dinner_insulin = None
                    
                # Bedtime
                if bedtime_carb is not None:
                    time = _dosageTime(bedtime_reading, bedtime_carb, new_user_range, behavior_score)
                    dosage = bedtime_carb.carb_reading / 8 # 1:8 insulin to carb ratio, arbitrary
                    
                    bedtime_insulin = Insulin.objects.create(user=new_user, dosage=dosage, record_datetime=time)
                    
                else:
                    bedtime_insulin = None
                   
        # Glucose and carbohydrate are subjective mg/dL & carb ranges
        # Insulin is the relative minutes for when the dosage was given compared to the carbohydrates
        # Insulin and carbohydrates have a repeated awful range for consistancy        
        ranges = { 'glucose': { 'perfect': [100, 120], 'good': [65, 160], 'bad': [50, 300], 'awful': [40, 400]},
                   'carbohydrate': { 'perfect': [20, 40], 'good': [30, 80], 'bad': [60, 150], 'awful': [60, 150]},
                   'insulin': { 'perfect': [-20, -10], 'good': [-10, 10], 'bad': [5, 15], 'awful': [5,15]}}
                   
        mealtime_ranges = { 'breakfast': [6,8],
                            'lunch': [11,13],
                            'dinner': [17,20],
                            'bedtime': [21,25],
                            'snack1': [9,10],
                            'snack2': [14,16]}
                          
        recording_categories = ['fasting', 'before breakfast', 'after breakfast', 'before lunch', 'after lunch', 'snacks', 'before dinner', 'after dinner']
        
        for category in recording_categories:
            RecordingCategory.objects.create(name=category)
        
        user_list = []
        for user_num in range(num_users):
            behavior_score = randint(0, 100)
            
            range_roll_value = randint(behavior_score, 100)
            if range_roll_value >= 90:
                user_range = 'perfect'
            elif range_roll_value >= 50:
                user_range = 'good'
            elif range_roll_value >= 10:
                user_range = 'bad'
            else:
                user_range = 'awful'
                
            user_list.append({'user_range': user_range, 'behavior_score': behavior_score})
            num_days = randint(1,5)
            
            _createUser(user_num, behavior_score, user_range, num_days)
            
        return user_list
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_list = cls.setUpTestData(3)
        print(User.objects.all())
        print(UserProfile.objects.all())
        print()
        print(Glucose.objects.all())
        print()
        print(Carbohydrate.objects.all())
        print()
        print(Insulin.objects.all())
        print()
        
        index = 0
        for user in cls.user_list:
            print(f'Username=test_user{index} & Password=testPassword{index}: {user}')
            index += 1
        
        
        