from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import sys
from contextlib import contextmanager


class ChromeIntegrationTest(StaticLiveServerTestCase):
    # Overwrite the console output in order to suppress unexplained errors  
    @staticmethod
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
        with cls.suppress_stderr():
            cls.selenium.quit()
            
        super().tearDownClass()