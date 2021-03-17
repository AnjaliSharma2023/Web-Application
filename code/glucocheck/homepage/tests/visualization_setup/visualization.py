from homepage.tests.visualization_setup.classes import SetupVisualizationDatasets

class TestData(SetupVisualizationDatasets):
    def test_something(self):
        print()
        print(f'Server url: {self.live_server_url}')
        input('Press enter to exit')
        print()