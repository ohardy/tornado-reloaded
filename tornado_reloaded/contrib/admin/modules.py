from tornado.web import UIModule
from tornado.web import async

from tornado_reloaded.contrib.admin.resources import site

class HeaderModule(UIModule):
    """docstring for HeaderModule"""
    @async
    def render(self, callback, *args, **kwargs):
        """docstring for render"""
        return self.render_string('header.html', callback, site=site)
        
class AttributesTableForModule(UIModule):
    """docstring for AttributesTableForModule"""
    def render(self, *args, **kwargs):
        return 'AttributesTableForModule'
        
class PartialModule(UIModule):
    @async
    def render(self, obj, partial, callback, *args, **kwargs):
        if hasattr(partial, 'template'):
            return self.render_string(partial.template, callback, obj=obj, partial=partial)
        
        return partial