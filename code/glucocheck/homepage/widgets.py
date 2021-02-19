from django import forms
from django.template import loader
from django.utils.safestring import mark_safe

def boolean_check(v):
    return not (v is False or v is None or v == '')

class CheckboxLink(forms.widgets.Input):
    template_name = 'widgets/CheckboxLink.html'
    input_type = 'checkbox'
    
    def get_context(self, name, value, attrs):
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
        super().__init__(attrs)
        
        # side text is the text in the <p> tags next to the checkbox
        self.side_text = "" if side_text is None else side_text
        # link text is the text to be hyperlinked
        self.link_text = "" if link_text is None else link_text
        # specifys a wrapping element for each element
        self.wrap_elem = wrap_elem
        # attributes for <p>, <a>, and wrapping element tags
        self.text_attrs = {} if text_attrs is None else text_attrs.copy()
        self.link_attrs = {'href':None} if link_attrs is None else link_attrs.copy()
        self.wrap_elem_attrs = {} if wrap_elem_attrs is None else wrap_elem_attrs.copy()
        
        # check_test is a callable that takes a value and returns True
        # if the checkbox should be checked for that value.
        self.check_test = boolean_check if check_test is None else check_test
        