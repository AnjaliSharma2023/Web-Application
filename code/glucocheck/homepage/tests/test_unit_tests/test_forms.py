from homepage.tests.test_unit_tests.classes import UnitTestForm
from homepage.forms import LoginForm, EmailInputForm, ResetPasswordForm, SignupForm, UserProfileForm
from django.contrib.auth.models import User
from datetime import date


class TestLoginForm(UnitTestForm):
    '''Sets up a clean database, initializes test data, and runs tests on the login form.
    
    Public methods:
    setUpTestData -- Initializes test data
    test_correct_login -- Tests form validity when given correct credentials
    test_incorrect_login -- Tests form validity when given incorrect credentials
    test_unathenticated_user -- Tests form validity when given credentials to an unauthenticated user
    '''

    @classmethod
    def setUpTestData(cls):
        '''Creates users for testing.
    
        Keyword arguments:
        cls -- the TestLoginForm class
        '''
        User.objects.create_user(username='someUser', password='somePassword')
        User.objects.create_user(username='unAuthUser', password='somePassword', is_active=False)
    
    def test_correct_login(self):
        '''Tests form validity when given the correct credentials.
    
        Keyword arguments:
        self -- the TestLoginForm object
        '''
        user_login = LoginForm(data={'username':'someUser', 'password':'somePassword'})
        self.assertTrue(user_login.is_valid())
    
    def test_incorrect_login(self):
        '''Tests the expected form error and the number of errors present when given incorrect credentials.
    
        Keyword arguments:
        self -- the TestLoginForm object
        '''
        user_login = LoginForm(data={'username':'someUser', 'password':'wrongPassword'})
        num_errors = self._get_num_errors(user_login)
        form_error = user_login.errors.as_data()['__all__'][0].message
        self.assertTrue(form_error == "Your username OR password is incorrect" and num_errors == 1)
    
    def test_unathenticated_user(self):
        '''Tests the expected form error and the number of errors present when given credentials to an unauthenticated user.
    
        Keyword arguments:
        self -- the TestLoginForm object
        '''
        user_login = LoginForm(data={'username':'unAuthUser', 'password':'somePassword'})
        num_errors = self._get_num_errors(user_login)
        form_error = user_login.errors.as_data()['__all__'][0].message
        self.assertTrue(form_error == "Your account is not authenticated, please click the link in your email" and num_errors == 1)
        
        
class TestEmailInputForm(UnitTestForm):
    '''Sets up a clean database, initializes test data, and runs tests on the email input form.
    
    Public methods:
    setUpTestData -- Initializes test data
    test_correct_email -- Tests form validity when given an email associated with a user
    test_wrong_email -- Tests form validity when given an email not associated with a user
    test_bad_format_email -- Tests form validity when given an improperly formatted email
    '''

    @classmethod
    def setUpTestData(cls):
        '''Creates users for testing.
    
        Keyword arguments:
        cls -- the TestEmailInputForm class
        '''
        User.objects.create_user(username='someUser', password='somePassword', email='email@gmail.com')
        
    def test_correct_email(self):
        '''Tests form validity when given an email associated with a user.
    
        Keyword arguments:
        self -- the TestEmailInputForm object
        '''
        email_input = EmailInputForm(data={'email':'email@gmail.com'})
        self.assertTrue(email_input.is_valid())
        
    def test_wrong_email(self):
        '''Tests the expected form error and the number of errors present when given an email not associated with a user.
    
        Keyword arguments:
        self -- the TestEmailInputForm object
        '''
        email_input = EmailInputForm(data={'email':'wrongEmail@gmail.com'})
        num_errors = self._get_num_errors(email_input)
        form_error = email_input.errors.as_data()['email'][0].message
        self.assertTrue(form_error == "This email is not associated with a user" and num_errors == 1)
        
    def test_bad_format_email(self):
        '''Tests the expected form error and the number of errors present when given an improperly formatted email.
    
        Keyword arguments:
        self -- the TestEmailInputForm object
        '''
        email_input = EmailInputForm(data={'email':'notAnEmail'})
        num_errors = self._get_num_errors(email_input)
        form_error = email_input.errors.as_data()['email'][0].message
        self.assertTrue(form_error == "Enter a valid email address." and num_errors == 1)
    
    
class TestResetPasswordForm(UnitTestForm):
    '''Sets up a clean database, initializes test data, and runs tests on the reset password form.
    
    Public methods:
    test_correct_passwords -- Tests form validity when matching and secure passwords
    test_mismatching_passwords -- Tests form validity when given mismatching passwords
    test_insecure_password -- Tests form validity when given insecure passwords
    '''
    
    def test_correct_passwords(self):
        '''Tests form validity when given matching and secure passwords.
    
        Keyword arguments:
        self -- the TestResetPasswordForm object
        '''
        password_input = ResetPasswordForm(data={'password1':'somePassword1', 'password2':'somePassword1'})
        self.assertTrue(password_input.is_valid())
        
    def test_mismatching_passwords(self):
        '''Tests the expected form error and the number of errors present when given mismatching passwords.
    
        Keyword arguments:
        self -- the TestResetPasswordForm object
        '''
        password_input = ResetPasswordForm(data={'password1':'somePassword1', 'password2':'anotherPassword1'})
        num_errors = self._get_num_errors(password_input)
        form_error = password_input.errors.as_data()['__all__'][0].message
        self.assertTrue(form_error == "The two password fields didn’t match." and num_errors == 1)
        
    def test_insecure_password(self):
        '''Tests the expected form error and the number of errors present when given insecure passwords.
        
        Passwords are insecure if they do not include at least 1 lowercase letter, 1 uppercase letter, and 1 number
    
        Keyword arguments:
        self -- the TestResetPasswordForm object
        '''
        password_input = ResetPasswordForm(data={'password1':'somepassword', 'password2':'somepassword'})
        num_errors = self._get_num_errors(password_input)
        form_error = password_input.errors.as_data()['__all__'][0].message
        self.assertTrue(form_error == 'Your password must be at least 6 letters long and contain at least one uppercase letter, one lowercase letter, and one digit' and num_errors == 1)


class TestSignupForm(UnitTestForm):
    '''Sets up a clean database, initializes test data, and runs tests on the signup form.
    
    Public methods:
    setUpTestData -- Initializes test data
    test_correct_input -- Tests form validity when given correct input
    test_incorrect_username -- Tests form validity when given a username already associated with a user
    test_incorrect_email -- Tests form validity when given an email already associated with a user
    test_bad_format_email -- Tests form validity when given an improperly formatted email
    test_mismatching_passwords -- Tests form validity when given mismatching passwords
    '''
    
    @classmethod
    def setUpTestData(cls):
        '''Creates users for testing.
    
        Keyword arguments:
        cls -- the TestSignupForm class
        '''
        User.objects.create_user(username='wrongUser', email='wrong@gmail.com', password='somePassword')

    def test_correct_input(self):
        '''Tests form validity when given correct input.
    
        Keyword arguments:
        self -- the TestSignupForm object
        '''
        username_input = SignupForm(data ={'username' : 'username', 'email':'test@gmail.com','password1': 'testPassword1','password2':'testPassword1'})
        self.assertTrue(username_input.is_valid())

    def test_incorrect_username(self):
        '''Tests the expected form error and the number of errors present when given a username already associated with a user.
    
        Keyword arguments:
        self -- the TestSignupForm object
        '''
        username_input = SignupForm(data ={'username' : 'wrongUser', 'email':'test@gmail.com','password1': 'testPassword1','password2':'testPassword1'})
        num_errors = self._get_num_errors(username_input)
        form_error = username_input.errors.as_data()['username'][0].message
        self.assertTrue(form_error == "A user with that username already exists." and num_errors == 1)

    def test_incorrect_email(self):
        '''Tests the expected form error and the number of errors present when given an email already associated with a user.
    
        Keyword arguments:
        self -- the TestSignupForm object
        '''
        signup_email_input = SignupForm(data ={'username' : 'username', 'email':'wrong@gmail.com','password1': 'testPassword1','password2':'testPassword1'})
        num_error = self._get_num_errors(signup_email_input)
        form_error = signup_email_input.errors.as_data()['email'][0].message
        self.assertTrue(form_error ==  'A user with that email already exists' and num_error ==1)

    def test_bad_format_email(self):
        '''Tests the expected form error and the number of errors present when given an improperly formatted email.
    
        Keyword arguments:
        self -- the TestSignupForm object
        '''
        signup_email_input = SignupForm(data ={'username' : 'username', 'email':'notAnEmail','password1': 'testPassword1','password2':'testPassword1'})
        num_errors = self._get_num_errors(signup_email_input)
        form_error = signup_email_input.errors.as_data()['email'][0].message
        self.assertTrue(form_error == "Enter a valid email address." and num_errors == 1)
        
    def test_mismatching_passwords(self):
        '''Tests the expected form error and the number of errors present when given mismatching passwords.
    
        Keyword arguments:
        self -- the TestSignupForm object
        '''
        signup_password_input = SignupForm(data ={'username' : 'username', 'email':'test@gmail.com','password1': 'somePassword1','password2':'anotherPassword1'})
        num_errors = self._get_num_errors(signup_password_input)
        form_error = signup_password_input.errors.as_data()['password2'][0].message
        self.assertTrue(form_error == "The two password fields didn’t match." and num_errors == 1)
        
    def test_insecure_password(self):
        '''Tests the expected form error and the number of errors present when given insecure passwords.
        
        Passwords are insecure if they do not include at least 1 lowercase letter, 1 uppercase letter, and 1 number
    
        Keyword arguments:
        self -- the TestSignupForm object
        '''
        signup_password_input = SignupForm(data ={'username' : 'username', 'email':'test@gmail.com','password1': 'insecurePassword','password2':'insecurePassword'})
        num_errors = self._get_num_errors(signup_password_input)
        form_error = signup_password_input.errors.as_data()['__all__'][0].message
        self.assertTrue(form_error == 'Your password must be at least 6 letters long and contain at least one uppercase letter, one lowercase letter, and one digit' and num_errors == 1)


class TestUserProfileForm(UnitTestForm):
    '''Sets up a clean database, initializes test data, and runs tests on the user profile form.
    
    Public methods:
    test_correct_birth_date -- Tests form validity when given a birth date signifying an age of over 18 years
    test_incorrect_birth_date -- Tests form validity when given a birth date signifying an age of under 18 years
    '''
    
    def test_correct_birth_date(self):
        '''Tests form validity when given a birth date signifying an age of over 18 years.
    
        Keyword arguments:
        self -- the TestUserProfileForm object
        '''
        birth_date = date.today()
        birth_date = birth_date.replace(year=date.today().year - 19)
        birth_date_input = UserProfileForm(data ={'birth_date':birth_date, 'state': 'New Jersey','signup_confirmation':True})
        self.assertTrue(birth_date_input.is_valid())
        
    def test_incorrect_birth_date(self):
        '''Tests the expected form error and the number of errors present when given a birth date signifying an age of under 18 years.
    
        Keyword arguments:
        self -- the TestUserProfileForm object
        '''
        birth_date = date.today()
        birth_date = birth_date.replace(year=date.today().year - 17)
        birth_date_input = UserProfileForm(data ={'birth_date':birth_date, 'state': 'New Jersey','signup_confirmation':True})
        num_errors = self._get_num_errors(birth_date_input)
        form_error = birth_date_input.errors.as_data()['birth_date'][0].message
        self.assertTrue(form_error == 'Must be at least 18 years old to register' and num_errors == 1)