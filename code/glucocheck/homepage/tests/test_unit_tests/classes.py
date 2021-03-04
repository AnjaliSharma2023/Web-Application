from django.test import TestCase


class UnitTestForm(TestCase):
    '''Sets up a clean database for unit tests.'''
    
    @staticmethod
    def _get_num_errors(form):
        '''Returns the number of errors found in a form object.
    
        Keyword arguments:
        form -- the form object to be parsed
        '''
        num_errors = 0
        for name, errors in form.errors.as_data().items():
            num_errors += len(errors)
        
        return num_errors