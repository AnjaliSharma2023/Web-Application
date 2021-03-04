from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import sys
from contextlib import contextmanager


class ChromeIntegrationTest(StaticLiveServerTestCase):
    '''Sets up a static live server, clean database, and selenium chrome browser for integration tests.
    
    Public methods:
    setUpClass -- Initializes the database, live server, and selenium chrome browser
    tearDownClass -- Destructs the database, live server and selenium chrome browser
    '''
    
    @staticmethod
    @contextmanager
    def _suppress_stderr():
        '''Suspends writes to stderr (pythons error output) temporarily to ensure a noise free shutdown process.
        
        This is done because the driver.quit() interaction on selenium with the django development environment
        produces lengthy ConnectionResetError messages that do not impact the validity of the tests.
        '''
        "Temporarly suppress writes to stderr"
        class Null:
            write = lambda *args: None
        err, sys.stderr = sys.stderr, Null
        try:
            yield
        finally:
            sys.stderr = err
    
    @classmethod
    def setUpClass(cls):
        '''Initializes the database, live server, and selenium chrome browser with options to hide uneccessary messages and run in headless mode.
    
        Keyword arguments:
        cls -- the ChromeIntegrationTest class
        '''
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
        '''Destructs the database, live server, and selenium chrome browser while suppressing .quit error messages.
    
        Keyword arguments:
        cls -- the ChromeIntegrationTest class
        '''
        with cls._suppress_stderr():
            cls.selenium.quit()
            
        super().tearDownClass()