from tornado.web import UIModule

from tornado_reloaded.contrib.admin.resources import site

class HeaderModule(UIModule):
    """docstring for HeaderModule"""
    def render(self, *args, **kwargs):
        """docstring for render"""
        return self.render_string('header.html', site=site)
        
class AttributesTableForModule(UIModule):
    """docstring for AttributesTableForModule"""
    def render(self, *args, **kwargs):
        return 'AttributesTableForModule'
        
class PartialModule(UIModule):
    def render(self, obj, partial, *args, **kwargs):
        if hasattr(partial, 'template'):
            return self.render_string(partial.template, obj=obj, partial=partial)
        
        return partial