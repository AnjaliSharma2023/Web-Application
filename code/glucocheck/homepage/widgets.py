from django import forms
from django.template import loader
from django.utils.safestring import mark_safe


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
    
    def get_context(self, name, value, attrs):
        '''Returns the context based on the __init__ input values.
    
        Keyword arguments:
        self -- the CheckboxLink object
        name -- the name of the <input> tag
        value -- the value of the <input> tag
        attrs -- the attributes of the <input> tag
        '''
        if self.check_test(value):
            attrs = {**(attrs or {}), 'checked': True}
            
        context = {
            'widget': {
                'name': name,
                'is_hidden': self.is_hidden,
                'required': self.is_required,
                'value': self.format_value(value),
                'attrs': self.build_attrs(self.attrs, attrs),
                'template_name': self.template_name,
                'text': {
                    'name': name + '_text',
                    'value': self.format_value(self.side_text),
                    'attrs': self.text_attrs,
                },
                'link': {
                    'name': name + '_link',
                    'value': self.format_value(self.link_text),
                    'attrs': self.link_attrs,
                },
                'wrap_elem': {
                    'name': name + '_wrap',
                    'tag': self.wrap_elem,
                    'attrs': self.wrap_elem_attrs,
                }
            },
        }
        context['widget']['type'] = self.input_type
        return context
        
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
        