from homepage.tests.test_integration_tests.classes import ChromeIntegrationTest
from time import sleep

class TestTemp(ChromeIntegrationTest):
    def test_display_homepage(self):
        self.selenium.get(self.live_server_url)
        sleep(2)