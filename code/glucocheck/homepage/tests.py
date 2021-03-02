from django.test import TestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from homepage.forms import LoginForm, ResetPasswordEmail, ResetPassword
from django.contrib.auth.models import User
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import sys
from contextlib import contextmanager

# Get the number of errors from a form
def get_num_errors(form):
    num_errors = 0
    for name, errors in form.errors.as_data().items():
        num_errors += len(errors)
    
    return num_errors
   
# Overwrite the console output in order to suppress unexplained errors  
@contextmanager
def suppress_stderr():
    "Temporarly suppress writes to stderr"
    class Null:
        write = lambda *args: None
    err, sys.stderr = sys.stderr, Null
    try:
        yield
    finally:
        sys.stderr = err
        
# Create your tests here.
class test_login_form_errors(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Creates users for testing
        User.objects.create_user(username='someUser', password='somePassword')
        User.objects.create_user(username='unAuthUser', password='somePassword', is_active=False)
    
    def test_correct_login(self):
        user_login = LoginForm(data={'username':'someUser', 'password':'somePassword'})
        self.assertTrue(user_login.is_valid())
    
    def test_incorrect_login(self):
        user_login = LoginForm(data={'username':'someUser', 'password':'wrongPassword'})
        # Gets the number of form errors
        num_errors = get_num_errors(user_login)
        # Gets the first error message from the top of the '__all__' item in the dictionary
        form_error = user_login.errors.as_data()['__all__'][0].message
        self.assertTrue(form_error == "Your username OR password is incorrect" and num_errors == 1)
    
    def test_unathenticated_user(self):
        user_login = LoginForm(data={'username':'unAuthUser', 'password':'somePassword'})
        num_errors = get_num_errors(user_login)
        form_error = user_login.errors.as_data()['__all__'][0].message
        self.assertTrue(form_error == "Your account is not authenticated, please click the link in your email" and num_errors == 1)
        
class test_forgot_password_email(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Creates users for testing
        User.objects.create_user(username='someUser', password='somePassword', email='email@gmail.com')
        
    def test_correct_email(self):
        email_input = ResetPasswordEmail(data={'email':'email@gmail.com'})
        self.assertTrue(email_input.is_valid())
        
    def test_wrong_email(self):
        email_input = ResetPasswordEmail(data={'email':'wrongEmail@gmail.com'})
        num_errors = get_num_errors(email_input)
        form_error = email_input.errors.as_data()['email'][0].message
        self.assertTrue(form_error == "This email is not associated with a user" and num_errors == 1)
        
    def test_bad_format_email(self):
        email_input = ResetPasswordEmail(data={'email':'notAnEmail'})
        num_errors = get_num_errors(email_input)
        form_error = email_input.errors.as_data()['email'][0].message
        self.assertTrue(form_error == "Enter a valid email address." and num_errors == 1)
        
class test_reset_password(TestCase):
    def test_correct_passwords(self):
        password_input = ResetPassword(data={'password1':'somePassword1', 'password2':'somePassword1'})
        self.assertTrue(password_input.is_valid())
        
    def test_mismatching_passwords(self):
        password_input = ResetPassword(data={'password1':'somePassword1', 'password2':'anotherPassword1'})
        num_errors = get_num_errors(password_input)
        form_error = password_input.errors.as_data()['__all__'][0].message
        self.assertTrue(form_error == "The two password fields didn’t match." and num_errors == 1)
        
    def test_insecure_password(self):
        password_input = ResetPassword(data={'password1':'somepassword', 'password2':'somepassword'})
        num_errors = get_num_errors(password_input)
        form_error = password_input.errors.as_data()['__all__'][0].message
        self.assertTrue(form_error == 'Your password must be at least 6 letters long and contain at least one uppercase letter, one lowercase letter, and one digit' and num_errors == 1)
        
class test_login_live(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        chrome_options = Options()
        # Option to suppress 'DevTools listening on...' message
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        # Set browser to headless
        chrome_options.headless = True
        cls.selenium = webdriver.Chrome(chrome_options=chrome_options)
        
        cls.selenium.implicitly_wait(10)
    
    @classmethod
    def tearDownClass(cls):
        with suppress_stderr():
            cls.selenium.quit()
            
        super().tearDownClass()
    
    def test_homepage(self):
        self.selenium.get(self.live_server_url)
        time.sleep(2)