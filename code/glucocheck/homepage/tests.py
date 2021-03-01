from django.test import TestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from homepage.forms import LoginForm, ResetPasswordEmail, ResetPassword, SignupForm, UserProfileForm
from django.contrib.auth.models import User
from datetime import date

def get_num_errors(form):
    num_errors = 0
    for name, errors in form.errors.as_data().items():
        num_errors += len(errors)
    
    return num_errors

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

# create a class that inherit from TestCase
class test_signup_form_errors(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Creates users for testing
        User.objects.create_user(username='username', email='wrong@gmail.com', password='somePassword')

    def test_correct_username(self):
        username_input = SignupForm(data ={'username' : 'userName', 'email':'test@gmail.com','password1': 'testPassword1','password2':'testPassword1'})
        self.assertTrue(username_input.is_valid())

    def test_incorrect_username(self):
        username_input = SignupForm(data ={'username' : 'username', 'email':'test@gmail.com','password1': 'testPassword1','password2':'testPassword1'})
        num_errors = get_num_errors(username_input)
        form_error = username_input.errors.as_data()['username'][0].message
        self.assertTrue(form_error == "A user with that username already exists." and num_errors == 1)


    def test_correct_signup_email(self):
        signup_email_input = SignupForm(data ={'username' : 'userName', 'email':'test@gmail.com','password1': 'testPassword1','password2':'testPassword1'})
        self.assertTrue(signup_email_input.is_valid())

    def test_incorrect_signup_email(self):
        signup_email_input = SignupForm(data ={'username' : 'userName', 'email':'wrong@gmail.com','password1': 'testPassword1','password2':'testPassword1'})
        num_error = get_num_errors(signup_email_input)
        form_error = signup_email_input.errors.as_data()['email'][0].message
        self.assertTrue(form_error ==  'A user with that email already exists' and num_error ==1)

        
    def test_bad_signup_format_email(self):
        signup_email_input = SignupForm(data ={'username' : 'userName', 'email':'notAnEmail','password1': 'testPassword1','password2':'testPassword1'})
        num_errors = get_num_errors(signup_email_input)
        form_error = signup_email_input.errors.as_data()['email'][0].message
        self.assertTrue(form_error == "Enter a valid email address." and num_errors == 1)


    def test_correct_signup_passwords(self):
        signup_password_input = SignupForm(data ={'username' : 'userName', 'email':'test@gmail.com','password1': 'somePassword1','password2':'somePassword1'})
        self.assertTrue(signup_password_input.is_valid())
        
    def test_mismatching_signup_passwords(self):
        signup_password_input = SignupForm(data ={'username' : 'userName', 'email':'test@gmail.com','password1': 'somePassword1','password2':'anotherPassword1'})
        num_errors = get_num_errors(signup_password_input)
        form_error = signup_password_input.errors.as_data()['password2'][0].message
        self.assertTrue(form_error == "The two password fields didn’t match." and num_errors == 1)
        
    def test_insecure_signup_password(self):
        signup_password_input = SignupForm(data ={'username' : 'userName', 'email':'test@gmail.com','password1': 'somepassword','password2':'somepassword'})
        num_errors = get_num_errors(signup_password_input)
        form_error = signup_password_input.errors.as_data()['__all__'][0].message
        self.assertTrue(form_error == 'Your password must be at least 6 letters long and contain at least one uppercase letter, one lowercase letter, and one digit' and num_errors == 1)

class test_birth_date(TestCase):

    def test_correct_birth_date(self):
        birth_date = date.today()
        birth_date = birth_date.replace(year=date.today().year - 19)
        birth_date_input = UserProfileForm(data ={'birth_date':birth_date, 'state': 'New Jersey','signup_confirmation':'True'})
        self.assertTrue(birth_date_input.is_valid())
        
    def test_incorrect_birth_date(self):
        birth_date = date.today()
        birth_date = birth_date.replace(year=date.today().year - 17)
        birth_date_input = UserProfileForm(data ={'birth_date':birth_date, 'state': 'New Jersey','signup_confirmation':'True'})
        num_errors = get_num_errors(birth_date_input)
        form_error = birth_date_input.errors.as_data()['birth_date'][0].message
        self.assertTrue(form_error == 'Must be at least 18 years old to register' and num_errors == 1)


    