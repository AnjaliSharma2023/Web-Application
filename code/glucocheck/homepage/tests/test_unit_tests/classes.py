from django.test import TestCase

class UnitTestForm(TestCase):
    # Get the number of errors from a form
    @staticmethod
    def get_num_errors(form):
        num_errors = 0
        for name, errors in form.errors.as_data().items():
            num_errors += len(errors)
        
        return num_errors