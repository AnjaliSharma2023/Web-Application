from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.contrib.auth.models import User
from django.db.utils import IntegrityError
from homepage.models import UserProfile, RecordingCategory, Glucose, Carbohydrate, Insulin
from datetime import datetime, date, timedelta
import pandas as pd
from random import randint, sample
from math import ceil


class SetupVisualizationDatasets(StaticLiveServerTestCase):
    '''A class for initializing test glucose, insulin, and carbohydrate data for multiple users in a live test server.
    
    Public methods:
    setUpTestData -- Generates test data for a number of users
    setUpClass -- Initializes the live tests server, database, and test data
    '''
    
    @staticmethod
    def setUpTestData(num_users):
        '''Adds a number of users and their associated glucose, insulin, and carbohydrate data to the database.
        
        Keyword Arguments:
        num_users -- the number of users to create
        '''
        def _getCategory(mealtime, behavior_score):
            '''Returns the glucose category based on the time of day and behavior score of the user.
            
            Keyword Arguments:
            mealtime -- a string with the name of the mealtime: [breakfast, snack1, lunch, snack2, dinner, bedtime]
            behavior_score -- the competency of the user: int 0-100 (inclusive)
            '''
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
            '''Returns the glucose range and time of reading.
            
            Keyword Arguments:
            prev_reading -- the model object of the previous reading, or None if there isn't one
            user_range -- a string with the name of the user's range: [perfect, good, bad, awful]
            day -- the day of the reading
            hour_range -- the hour range the reading can be within, effectively [x, y+1] due to the random number of minutes added
            '''
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
            '''Returns the carbohydrate range and time of reading.
            
            Keyword Arguments:
            glucose_reading -- the model object of the associated glucose reading, or None if there isn't one
            user_range -- a string with the name of the user's range: [perfect, good, bad, awful]
            day -- the day of the reading
            hour_range -- the hour range the reading can be within, effectively [x, y+1] due to the random number of minutes added
            behavior_score -- the competency of the user: int 0-100 (inclusive)
            '''
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
            '''Returns the time of the insulin dosage.
            
            Keyword Arguments:
            glucose_reading -- the model object of the associated glucose reading, or None if there isn't one
            carbohydrate_reading -- the model object of the associated carbohydrate reading, or None if there isn't one
            user_range -- a string with the name of the user's range: [perfect, good, bad, awful]
            behavior_score -- the competency of the user: int 0-100 (inclusive)
            '''
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
            '''Creates a user in the database, with the user_num denoting the user, and returns a list with the user behavior score and range.
            
            Keyword Arguments:
            user_num -- the number of the user, appended to the username and password
            behavior_score -- the competency of the user: int 0-100 (inclusive)
            new_user_range -- a string with the name of the user's range: [perfect, good, bad, awful]
            num_days -- the number of days to fill glucose, insulin, and carbohydrate data for
            '''
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
            if range_roll_value >= 95:
                user_range = 'perfect'
            elif range_roll_value >= 70:
                user_range = 'good'
            elif range_roll_value >= 30:
                user_range = 'bad'
            else:
                user_range = 'awful'
                
            user_list.append({'user_range': user_range, 'behavior_score': behavior_score})
            num_days = randint(1,10)
            
            _createUser(user_num, behavior_score, user_range, num_days)
            
        return user_list
    
    class setUpTrendData:
        # 285 carbs per day # normal 200/275
        def __init__(self, num_users):
            self.statements = ['normal', 'up_basal', 'down_basal', 'up_bolus', 'down_bolus', 'earlier_bolus', 'lower_daily_carbs', 'lower_mealtime_carbs']
            # Glucose:
            #   {'initial_value,</>/=,subsequent_value,</>/=,timeframe(H:MM)':tally_value} timeframe is optional for when there is no fasting/snack reading in between meals
            #   1.5 prepended to intial_value signifies the reading is in the snack/fasting time zone
            #   subsequent_value has an x+- value next to it in the case that 3 values must be tested to match a trend, the third tests within an even range
            # Carbs:
            #   {'carb_value,</>/=,comparison_value,</>/=,timeframe(H:MM)':tally_value'} 
            #   If timeframe is not filled the carb value applies to a single meal time
            self.trends = {self.statements[0]:{'x,=,x+-10,0/85':1}, self.statements[1]:{'1.5x,>,x+-10,x+20/25,>,1:30':1, 'x,>,x+30/50':.5}, self.statements[2]:{'1.5x,<,x+-10,x-20/25,>,1:30':1, 'x,<,40/80,>,1:30':.5, 'x,<,x-30/50':.5}, 
            self.statements[3]:{'x,>,x+15/25,>,1:30':1, 'x,>,x+30/50':.5}, self.statements[4]:{'x,<,40/80,<,1:30':1, 'x,<,x-15/25,>,1:30':1, 'x,<,40/80,>,1:30':.5, 'x,<,x-30/50':.5}, 
            self.statements[5]:{'x,>,x+50/80,x+-15,<,1:30':1}, self.statements[6]:{'x,>,275/300,=,24:00':1}, self.statements[7]:{'x,>,90/100':1}}
            
            self.mealtime_ranges = { 'breakfast': [6,8],
                                'inbetween1': [9,10],
                                'lunch': [11,13],
                                'inbetween2': [14,16],
                                'dinner': [17,20],
                                'bedtime': [21,25]}
                                
            # Fill the RecordingCategory database
            self._fillCategories()
            
            # Create and fill the user list
            user_num = 0
            created_users = 0
            user_list = []
            while created_users < num_users:
                user, user_num = self._createUser(user_num)
                user_list.append(user)
                created_users += 1
                
            # Fill user data according to specified trends on a day by day basis with full entry
            seperated_ranges = [[self.mealtime_ranges['breakfast'], self.mealtime_ranges['inbetween1'], self.mealtime_ranges['lunch']], [self.mealtime_ranges['lunch'], self.mealtime_ranges['inbetween2'], self.mealtime_ranges['dinner']], [self.mealtime_ranges['dinner'], None, self.mealtime_ranges['bedtime']]]
            
            # Seperate glucose and carb trend groups
            glucose_trend_group_1_and_2 = {}
            glucose_trend_group_3 = {}
            
            carbs_trend_group = {}
            for key, value in self.trends.items():
                # Glucose
                if key in self.statements[:6]:
                    for key2, value2 in value.items():
                        # Groups 1 and 2
                        if key in glucose_trend_group_1_and_2.keys():
                            glucose_trend_group_1_and_2[key].append([key2, value2])
                        else:
                            glucose_trend_group_1_and_2[key] = [[key2, value2]]
                        # Group 3
                        if len(key2.split(',')) < 5:
                            if key in glucose_trend_group_3.keys():
                                glucose_trend_group_3[key].append([key2, value2])
                            else:
                                glucose_trend_group_3[key] = [[key2, value2]]
                # Carbs
                if key in self.statements[6:] or key == self.statements[0]:
                    for key2, value2, in value.items():
                        if key in carbs_trend_group.keys():
                            carbs_trend_group[key].append([key2, value2])
                        else:
                            carbs_trend_group[key] = [[key2, value2]]
            
            self.return_dict = {}
            start_date = date.today() - timedelta(days=180)
            user_num = 0
            for user in user_list:
                # Bound chance 30% to 60%
                chance = randint(30,60)
                user_trends = self._getUserTrends(user_num)
                user_num += 1
                for day in pd.date_range(start=start_date, end=date.today()).to_pydatetime():
                    glucose_readings = [None for x in range(3)]
                    days_readings = [None]
                    for index in range(len(seperated_ranges)):
                        if index == 2:
                            glucose_trend = self._determineTrend(glucose_trend_group_3, user_trends, chance)
                        else:
                            glucose_trend = self._determineTrend(glucose_trend_group_1_and_2, user_trends, chance)
                                
                        glucose_readings = self._addGlucoseData(user, glucose_trend, day, seperated_ranges[index], glucose_readings[-1])
                        if days_readings[-1] == None:
                            days_readings[-1] = glucose_readings[0]
                        
                        days_readings = days_readings + glucose_readings[1:]
                    
                    
                    carb_trend = self._determineTrend(carbs_trend_group, user_trends, chance, False)
                    norm_trend = self._switchNormal(list(self.trends[self.statements[0]])[0], False)
                    self._addCarbData(user, carb_trend, norm_trend, day, days_readings)
                
                percent_filled = sum([value for key in user_trends.keys() for value in user_trends[key].values()])
                percent_filled = ((percent_filled - user_trends["active"]["normal"]) /  percent_filled) * 100
                self.return_dict[str(user)] = {'trends, occurences':user_trends, '% Chance':f'{chance}%', '% Filled':f'{percent_filled:.0f}%'}
            
                
        def __str__(self):
            return_string = '\n'
            for key, value in self.return_dict.items():
                return_string += f'{key}: {value}\n\n'
                
            return return_string[:-2]
        
        
        @staticmethod
        def _switchNormal(trend, glucose):
            trend = trend.split(',')
            if glucose is False:
                trend[-2] = trend[-1]
                
            return ",".join(trend[:-1])
        
        
        @staticmethod
        def _createUser(user_num):
            '''Creates and returns new users, ensuring there are no database conflicts.
            
            Keyword Arguments:
            user_num -- the user num to appended to the username, password, and email and then incremented and returned
            '''
            birth_date = datetime.today().replace(year=datetime.today().year - 19)
            while True:
                try:
                    new_user = User.objects.create_user(username=f'test_user{user_num}', password=f'testPassword{user_num}', email=f'testEmail{user_num}@gmail.com')
                    break
                except IntegrityError:
                    user_num += 1
            
            new_user_profile = UserProfile.objects.create(user=new_user, birth_date=birth_date, state='Arizona')
            
            user_num += 1
            return new_user, user_num
            
            
        @staticmethod
        def _fillCategories():
            recording_categories = ['fasting', 'before breakfast', 'after breakfast', 'before lunch', 'after lunch', 'snacks', 'before dinner', 'after dinner']
            if len(RecordingCategory.objects.all()) == 0:
                for category in recording_categories:
                    RecordingCategory.objects.create(name=category)
            
            
        def _getCategory(self, trend, time_ranges, time, inbetween=False):
            if inbetween:
                return RecordingCategory.objects.get(pk=6)
            
            time_ranges = {key:value for key, value in self.mealtime_ranges.items() if value in time_ranges}
            for key, value in time_ranges.items():
                if value[1] > 23:
                    if time.hour <= 2 or (time.hour >= value[0] and time.hour <= 23):
                        time = key
                        break
                else:
                    if time.hour <= value[1] and time.hour >= value[0]:
                        time = key
                        break
                    
            
            if 'bedtime' in time:
                return RecordingCategory.objects.get(pk=6)
            
            categories = RecordingCategory.objects.filter(name__icontains=key)        
            if (len(trend) == 6 or len(trend) == 3) and '1.5' not in trend[0]:
                chance = randint(0,100)
                if chance > 30:
                    return categories[0]
                else:
                    return categories[1]
            
            else:
                return categories[0]
          
          
        @staticmethod    
        def _getGlucoseTime(day, time_range, prev_reading=None, trend=None):
            if trend is None:
                hour = randint(time_range[0],time_range[1])
                if hour > 23:
                    hour -= 24
                    day = day + timedelta(days=1)
                
                time = day.replace(hour=hour, minute=randint(0,59), second=randint(0,59))
            else:
                trend[1] = trend[1].split(':')
                if trend[0] == '<':
                    hour = randint(0, int(trend[1][0]))
                    minute = randint(0, int(trend[1][1]))
                    
                    time = (prev_reading.record_datetime + timedelta(hours=hour, minutes=minute)).replace(second=randint(0,59))
                else:
                    time = prev_reading.record_datetime + timedelta(hours=int(trend[1][0]), minutes=int(trend[1][1]))
                    hour = randint(time.hour, time_range[1])
                    hour = 14
                    if hour == time.hour:
                        minute = randint(time.minute, 59)
                    else:
                        minute = randint(0, 59)
                    
                    time = day.replace(hour=hour, minute=minute, second=randint(0,59))
                    
            return time
             
             
        @staticmethod            
        def _getTrendReading(passthrough_vars, trend):
            reading_range = trend.split('/')

            if 'x' in trend:
                index = 0
                for char in reading_range[0][::-1]:
                    if char.isnumeric() is False:
                        index = len(reading_range[0]) - index
                        break
                    index += 1
                    
                trend = trend[:index]
                reading_range[0] = reading_range[0][index:]
                
                trend = trend.replace('x', passthrough_vars[0] + '.glucose_reading')
                passthrough_vars = {passthrough_vars[0]:passthrough_vars[1]}
                if '+-' in trend:
                    if len(reading_range) == 1:
                        reading_range.append('')
                    temp_var = reading_range[0]
                    reading_range[0] = eval(trend[:-2] + '-' + temp_var, passthrough_vars)
                    reading_range[1] = eval(trend[:-1] + temp_var, passthrough_vars)
                elif '-' in trend:
                    temp_var = reading_range[0]
                    reading_range[0] = eval(trend + reading_range[1], passthrough_vars)
                    reading_range[1] = eval(trend + temp_var, passthrough_vars)
                elif '+' in trend:
                    reading_range[0] = eval(trend + reading_range[0], passthrough_vars)
                    reading_range[1] = eval(trend + reading_range[1], passthrough_vars)
            else:
                reading_range = [int(x) for x in reading_range]
                
            return randint(reading_range[0], reading_range[1])
            
           
        def _addGlucoseData(self, user, trend, day, time_ranges, initial_reading=None):
            '''Creates 1 to 3 glucose data points from meal to meal, returning the last.
            
            Keywork Arguments:
            user -- the user object to attach data to
            trend -- the trend to generate the data in compience to
            day -- the datetime day the readings occur on
            time_ranges -- a 3 length list with time ranges for each potential value
            initial_reading -- the reading object returned from the last function call
            '''
            trend = trend.split(',')
            inbetween_reading = None
            next_reading = None
            sub_reading_used = False
            if initial_reading is None:
                reading = randint(80,160)
                time = self._getGlucoseTime(day, time_ranges[0])
                category = self._getCategory(trend, time_ranges, time)
                initial_reading = Glucose.objects.create(user=user, glucose_reading=reading, record_datetime=time, categories=category, notes="")
            elif initial_reading.glucose_reading < 80:
                initial_reading = Glucose.objects.create(user=user, glucose_reading=randint(80,160), record_datetime=initial_reading.record_datetime, categories=initial_reading.categories, notes="")
                sub_reading_used = True
                    
            if '1.5' in trend[0]:
                reading = self._getTrendReading(['initial_reading',initial_reading], trend[2])
                time = self._getGlucoseTime(day, time_ranges[1], initial_reading, trend[-2:])
                category = self._getCategory(trend, time_ranges, time, True)
                inbetween_reading = Glucose.objects.create(user=user, glucose_reading=reading, record_datetime=time, categories=category, notes="")
                
                reading = self._getTrendReading(['inbetween_reading',inbetween_reading], trend[3])
                time = self._getGlucoseTime(day, time_ranges[2])
                category = self._getCategory(trend, time_ranges, time)
                next_reading = Glucose.objects.create(user=user, glucose_reading=reading, record_datetime=time, categories=category, notes="")
            
            elif len(trend) < 4:
                reading = self._getTrendReading(['initial_reading',initial_reading], trend[2])
                time = self._getGlucoseTime(day, time_ranges[2])
                category = self._getCategory(trend, time_ranges, time)
                next_reading = Glucose.objects.create(user=user, glucose_reading=reading, record_datetime=time, categories=category, notes="")
            
            elif len(trend) < 6:
                reading = self._getTrendReading(['initial_reading',initial_reading], trend[2])
                time = self._getGlucoseTime(day, time_ranges[1], initial_reading, trend[-2:])
                category = self._getCategory(trend, time_ranges, time, True)
                inbetween_reading = Glucose.objects.create(user=user, glucose_reading=reading, record_datetime=time, categories=category, notes="")
                
            else:
                reading = self._getTrendReading(['initial_reading',initial_reading], trend[2])
                time = self._getGlucoseTime(day, time_ranges[1], initial_reading, trend[-2:])
                category = self._getCategory(trend, time_ranges, time, True)
                inbetween_reading = Glucose.objects.create(user=user, glucose_reading=reading, record_datetime=time, categories=category, notes="")
                
                reading = self._getTrendReading(['initial_reading',initial_reading], trend[3])
                time = self._getGlucoseTime(day, time_ranges[2])
                category = self._getCategory(trend, time_ranges, time)
                next_reading = Glucose.objects.create(user=user, glucose_reading=reading, record_datetime=time, categories=category, notes="")
            
            if sub_reading_used is True:
                initial_reading.delete()
                
            return [initial_reading, inbetween_reading, next_reading]
              
              
        @staticmethod
        def _getCarbTime(glucose_reading):
            category = glucose_reading.categories.name
            time = glucose_reading.record_datetime
            if 'snacks' in category or 'before' in category:
                return time + timedelta(minutes=randint(0,4), seconds=randint(0,59))
                
            elif 'after' in category:
                return time - timedelta(minutes=randint(0,4), seconds=randint(0,59))
        
        
        @staticmethod
        def _format24HCarbTrend(trend):
            low = int(trend.split('/')[0])
            high = int(trend.split('/')[1])
            
            low = str(low // 3)
            high = str(high // 3)
            
            return '/'.join([low, high])
            
       
        def _addCarbData(self, user, trend, norm_trend, day, glucose_readings):
            # Carb readings for inbetween readings that are low dependent on time
            # Carb readings for low bedtime values 
            
            # Fasting = RecordingCategory.objects.get(pk=1)
            trend = trend.split(',')
            norm_trend = norm_trend.split(',')
            # Normal and day over range
            fasting_category = None
            carb_readings = [None for x in range(len(glucose_readings))]
            insulin_readings = [None for x in range(len(glucose_readings))]
            count_trend = 0
            if trend != norm_trend and len(trend) < 4:
                count_trend = sample([0,2,4], randint(1,3))
                
            for index in range(len(glucose_readings)):
                if index % 2 == 0:
                    if count_trend == 0 and len(trend) < 4:
                        carb_reading = self._getTrendReading([], trend[2])
                    elif count_trend == 0:
                        carb_reading = self._getTrendReading([], self._format24HCarbTrend(trend[2]))
                    elif index in count_trend:
                        carb_reading = self._getTrendReading([], trend[2])
                    else:
                        carb_reading = self._getTrendReading([], norm_trend[2])
                
                    record_datetime = self._getCarbTime(glucose_readings[index])
                    carb_readings[index] = Carbohydrate.objects.create(user=user, carb_reading=carb_reading, record_datetime=record_datetime)
                    
                    record_datetime = record_datetime - timedelta(minutes=randint(0,1), seconds=randint(0,59))
                    dosage = carb_reading / 8
                    insulin_readings[index] = Insulin.objects.create(user=user, dosage=dosage, record_datetime=record_datetime)
                    
                elif glucose_readings[index] is not None:
                    # Change category to be fasting when not low
                    if glucose_readings[index].glucose_reading >= 80:
                        if fasting_category is None:
                            fasting_category = RecordingCategory.objects.get(pk=1)
                            
                        glucose_readings[index].categories = fasting_category
                        glucose_readings[index].save()
                    # Fill low blood sugar carb values
                    else:
                        carb_reading = randint(15,20)
                        record_datetime = self._getCarbTime(glucose_readings[index])
                        carb_readings[index] = Carbohydrate.objects.create(user=user, carb_reading=carb_reading, record_datetime=record_datetime)
                
                
        @staticmethod
        def _returnCounterpart(item):
            item = item.split('_')
            if item[1] == 'basal':
                return item[0] + '_bolus'
            else:
                return item[0] + '_basal'
        
        
        def _getUserTrends(self, user_num):
            user_trends = {'active':{statement:0 for statement in self.statements[1:] if randint(0,100) <= 30}}
            user_trends['active'][self.statements[0]] = 0
            # ['normal', 'up_basal', 'down_basal', 'up_bolus', 'down_bolus', 'earlier_bolus', 'lower_daily_carbs', 'lower_mealtime_carbs']
            trends = [{'up_basal':0, 'up_bolus':0}, {'down_basal':0}, {'earlier_bolus':0}, {'lower_daily_carbs':0}, {'lower_mealtime_carbs':0}]
            
            user_trends = {'active': trends[user_num]}
            user_trends['inactive'] = {self._returnCounterpart(item):0 for item in user_trends['active'].keys() if ('up' in item or 'down' in item) and self._returnCounterpart(item) not in user_trends['active'].keys()}
            user_trends['active'][self.statements[0]] = 0
            
            return user_trends
        
        
        def _determineTrend(self, trend_group, user_trends, user_chance, glucose=True):
            temp_trends = [trend for trend in user_trends['active'].keys() if trend in trend_group.keys()]
            temp_trends.insert(0, temp_trends.pop(temp_trends.index('normal')))
            
            if user_chance < randint(0,100) or len(temp_trends) == 1:
                trend = trend_group[temp_trends[0]][0][0]
                trend = self._switchNormal(trend, glucose)
                user_trends['active'][temp_trends[0]] += 1
            else:
                key = randint(1,len(temp_trends)-1)
                
                trend = trend_group[temp_trends[key]]
                trend = trend[randint(0,len(trend)-1)][0]
                
                user_trends['active'][temp_trends[key]] += 1
                for item in trend_group[temp_trends[key]]:
                    if item[0] == trend:
                        increment = item[1]
                        break
                
                user_trends['active'][temp_trends[key]] += increment
                if increment == .5:
                    if self._returnCounterpart(temp_trends[key]) in user_trends['active'].keys():
                        user_trends['active'][self._returnCounterpart(temp_trends[key])] += increment
                    else:
                        user_trends['inactive'][self._returnCounterpart(temp_trends[key])] += increment
                
            return trend
            
    
    @classmethod
    def setUpClass(cls):
        '''Initializes the live server, database, testdata, and prints the user list.
        
        Keyword Arguments:
        cls -- the associated class of the method
        '''
        super().setUpClass()
        #cls.user_list = cls.setUpTestData(3)
        print(cls.setUpTrendData(5))
        '''
        
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
        '''
        
        
        