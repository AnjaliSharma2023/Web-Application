from django import forms


class FloatWithUnitField(forms.FloatField):
    '''A field to return a float value with unit string attached as a tuple.
    
    Public methods:
    to_python -- returns the input values converted to python objects
    clean -- cleans and returns the input values
    '''
    def to_python(self, value):
        '''Returns the input values as a tuple, converting the float value from a string
    
        Keyword arguments:
        self -- the FloatWithUnitField object
        value -- the list containing the float and unit as strings
        '''
        unit = value[-1]
        value = value[0]
        return super().to_python(value), unit
        
    def clean(self, value):
        '''Cleans the input values, raising ValidationErrors if the input is improper
    
        Keyword arguments:
        self -- the FloatWithUnitField object
        value -- the list containing the float and unit as strings
        '''
        value = self.to_python(value)
        self.validate(value[0])
        self.run_validators(value[0])
        return value
        


class IntWithUnitField(forms.IntegerField):
    '''A field to return an integer value with unit string attached as a tuple.
    
    Public methods:
    to_python -- returns the input values converted to python objects
    clean -- cleans and returns the input values
    '''
    def to_python(self, value):
        '''Returns the input values as a tuple, converting the integer value from a string
    
        Keyword arguments:
        self -- the IntWithUnitField object
        value -- the list containing the integer and unit as strings
        '''
        unit = value[-1]
        value = value[0]
        return super().to_python(value), unit
        
    def clean(self, value):
        '''Cleans the input values, raising ValidationErrors if the input is improper
    
        Keyword arguments:
        self -- the IntWithUnitField object
        value -- the list containing the integer and unit as strings
        '''
        value = self.to_python(value)
        self.validate(value[0])
        self.run_validators(value[0])
        return value