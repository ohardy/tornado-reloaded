from functools import partial
from cStringIO import StringIO

def html_tag(tag_name, self_closed=False, *args, **kwargs):
    """docstring for html_tag"""
    res = StringIO()
    w = res.write
    w('<%s' % (tag_name, ))
    
    attributes = [k for k in kwargs if not isinstance(kwargs[k], bool)]
    w(''.join(
        [' %s="%s"' % (k.replace('_', '-'), kwargs[k]) for k in attributes]
    ))
    
    attributes = [k for k in kwargs if isinstance(kwargs[k], bool)]
    w(''.join(
        [' %s="%s"' % (k.replace('_', '-'), k.replace('_', '-')) for k in attributes]
    ))
    
    
    attributes = [k for k in args if self.args[k] is True]
    w(''.join([' %s="%s"' % (k, k,) for k in attributes]))
    w('>')
    
    return res.getvalue()
    
def ul(*args, **kwargs):
    """docstring for ul"""
    return html_tag('ul', *args, **kwargs)
    
def li(*args, **kwargs):
    """docstring for ul"""
    return html_tag('li', *args, **kwargs)

def a(*args, **kwargs):
    """docstring for ul"""
    return html_tag('a', *args, **kwargs)

def span(*args, **kwargs):
    """docstring for ul"""
    return html_tag('span', *args, **kwargs)

def p(*args, **kwargs):
    """docstring for ul"""
    return html_tag('p', *args, **kwargs)

def article(*args, **kwargs):
    """docstring for ul"""
    return html_tag('article', *args, **kwargs)

def section(*args, **kwargs):
    """docstring for ul"""
    return html_tag('section', *args, **kwargs)

def strong(*args, **kwargs):
    """docstring for ul"""
    return html_tag('strong', *args, **kwargs)

def em(*args, **kwargs):
    """docstring for ul"""
    return html_tag('em', *args, **kwargs)

def header(*args, **kwargs):
    """docstring for ul"""
    return html_tag('header', *args, **kwargs)

def footer(*args, **kwargs):
    """docstring for ul"""
    return html_tag('footer', *args, **kwargs)
