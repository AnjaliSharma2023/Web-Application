from django import forms
from django.template import loader
from django.utils.safestring import mark_safe

class DateTimeLocal(forms.DateTimeInput):
    '''Overrides the DateTimeInput input_type attribute to display a datetime picker in chrome.
    
    input_type -- the input type to be used in the <input> tag
    '''
    input_type='datetime-local'

class CheckboxLink(forms.widgets.Input):
    '''Creates a checkbox widget with text and/or a hyperlink next to it.
    
    Public methods:
    get_context -- fills the context from the input values for the html template
    
    Instance variables:
    template_name -- a link to the widget html, to be programatically filled through the context and django template system
    input_type -- the input type to be used in the <input> tag
    '''
    template_name = 'widgets/CheckboxLink.html'
    input_type = 'checkbox'
    
    @staticmethod
    def _boolean_check(v):
        '''Checks the <input> tag return and returns a boolean value.
    
        Keyword arguments:
        v -- the <input> tag return value
        '''
        return not (v is False or v is None or v == '')
        
    def __init__(self, attrs=None, check_test=None, wrap_elem=None, wrap_elem_attrs=None, side_text=None, link_text=None, text_attrs=None, link_attrs=None):
        '''Initializes the input values in order to fill the context.
    
        Keyword arguments:
        self -- the CheckboxLink object
        attrs -- the optional attributes of the <input> element
        check_test -- the test to be run on the <input> element return value
        wrap_elem -- the optional element to be wrapped around the <input> element and the <p> element which wraps the optional <a> element
        side_text -- the text to be placed in the <p> element
        link_text -- the text to be placed in the <a> element if an href attribute is specified
        text_attrs -- the optional attributes of the <p> element
        link_attrs -- the attributes of the <a> hyperlink element, the 'href' value must be specified if this is to be included
        '''
        super().__init__(attrs)
        self.side_text = "" if side_text is None else side_text
        self.link_text = "" if link_text is None else link_text
        self.wrap_elem = wrap_elem
        self.text_attrs = {} if text_attrs is None else text_attrs.copy()
        self.wrap_elem_attrs = {} if wrap_elem_attrs is None else wrap_elem_attrs.copy()
        
        if link_attrs is None or 'href' not in link_attrs.keys():
            self.link_attrs = {'href':None}
        else:
            self.link_attrs = link_attrs.copy()
        
        
        self.check_test = self._boolean_check if check_test is None else check_test
        
    
    def get_context(self, name, value, attrs):
        '''Returns the context based on the __init__ input values.
    
        Keyword arguments:
        self -- the CheckboxLink object
        name -- the name of the form field object
        value -- the value of the widget
        attrs -- the general attributes of the widget
        '''
        text_context = {
                    'name': name + '_text',
                    'value': self.format_value(self.side_text),
                    'attrs': self.text_attrs,
                }
        
        link_context = {
                    'name': name + '_link',
                    'value': self.format_value(self.link_text),
                    'attrs': self.link_attrs,
                }
                
        wrap_elem_context = {
                    'name': name + '_wrap',
                    'tag': self.wrap_elem,
                    'attrs': self.wrap_elem_attrs,
                }
                
        if self.check_test(value):
            attrs = {**(attrs or {}), 'checked': True}
            
        context = super().get_context(name, value, attrs)
        
        context['text'] = text_context
        context['link'] = link_context
        context['wrap_elem'] = wrap_elem_context
        
        return context
        
        
class InputWithSelector(forms.widgets.MultiWidget):
    '''Creates the inputted widget with a selection box next to it.
    
    Public methods:
    decompress -- decompresses return values into a list if they are not already returned as such
    get_context -- fills the context from the input values for the html template
    
    Instance variables:
    template_name -- a link to the widget html, to be programatically filled through the context and django template system
    '''
    template_name = 'widgets/InputWithSelector.html'

    def __init__(self, widget, choices, attrs=None, wrap_elem=None, wrap_elem_attrs=None, selector_attrs=None):
        '''Initializes the InputWithSelector object.
        
        Keyword arguments:
        self -- the InputWithSelector object
        widget -- the input widget to be used
        choices -- the choices to be used in the forms.Select widget
        attrs -- the attributes to be applied to the input widget
        wrap_elem -- an optional wrapping element that surrounds the input element and the select element
        wrap_elem_attrs -- optional attributes to be applied to the wrapping widget
        selector_attrs -- optional attributes to be applied to the select widget
        '''
        _widgets = {'input':widget, 'selector':forms.Select(choices=choices, attrs=selector_attrs)}
        
        self.wrap_elem = wrap_elem
        self.wrap_elem_attrs = {} if wrap_elem_attrs is None else wrap_elem_attrs.copy()
        
        super().__init__(_widgets, attrs)
        
    def decompress(self, value):
        '''Decompresses value object from return if it is not passed as a list, unapplicable in this case so it always returns None.
        
        Keyword arguments:
        value -- the value to be decompressed and returned as a list
        '''
        return [None]
        
    def get_context(self, name, value, attrs):
        '''Returns the context based on the __init__ input values and subwidgets, removing the self.attrs keys from the select widgets attribute dict.
        
        Keyword Arguments:
        self -- the InputWithSelector object
        name -- the name of the form field object
        value -- the value of the widgets
        attrs -- the general attributes of the widgets
        '''
        context = super().get_context(name, value, attrs)
        
        wrap_elem_context = {
                    'name': name + '_wrap',
                    'tag': self.wrap_elem,
                    'attrs': self.wrap_elem_attrs,
                }
                
        context['wrap_elem'] = wrap_elem_context
        
        for name in self.attrs.keys():
            del context['widget']['subwidgets'][1]['attrs'][name]
           
        return context
        