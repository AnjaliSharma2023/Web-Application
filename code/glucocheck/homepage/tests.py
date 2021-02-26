from django.test import TestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from homepage.forms import LoginForm
from django.contrib.auth.models import User

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
        num_errors = len(user_login.errors.as_data()['__all__'])
        # Gets the first error message from the top of the '__all__' item in the dictionary
        form_error = user_login.errors.as_data()['__all__'][0].message
        self.assertTrue(form_error == "Your username OR password is incorrect" and num_errors == 1)
    
    def test_unathenticated_user(self):
        user_login = LoginForm(data={'username':'unAuthUser', 'password':'somePassword'})
        num_errors = len(user_login.errors.as_data()['__all__'])
        form_error = user_login.errors.as_data()['__all__'][0].message
        self.assertTrue(form_error == "Your account is not authenticated, please click the link in your email" and num_errors == 1)