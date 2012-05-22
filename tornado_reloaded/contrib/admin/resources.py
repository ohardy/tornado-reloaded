# -*- coding: utf-8 -*-
# encoding: utf-8
"""
__init__.py

Created by Olivier Hardy on 2012-04-17.
Copyright (c) 2012 Olivier Hardy. All rights reserved.
"""
import os

# from tornado_reloaded.contrib.admin.utils import column
# from tornado_reloaded.contrib.admin.utils import panel
from tornado_reloaded.db.orm.documents import loading

# from tornado_reloaded.contrib.admin.modules import AttributesTableForModule

class Column(object):
    """docstring for Column"""
    def __init__(self, name, field, sortable=None, uid=None, i18n=False):
        super(Column, self).__init__()
        self.name = name
        self.field = field
        self.sortable = sortable
        self.uid = uid
        self.i18n = i18n
        
class Panel(object):
    """docstring for Panel"""
    def __init__(self, name, uid):
        self.name = name
        self.uid = uid

class AttributesTableFor(object):
    """docstring for AttributesTableFor"""
    template = 'partial/attributes_table_for.html'
    def __init__(self, hander, obj, rows):
        self.hander = hander
        self.obj = obj
        self.rows = rows
        
    def render(self, handler):
        """docstring for render"""
        return 'AttributesTableFor.render'
        
class Sidebar(object):
    """docstring for Sidebar"""
    def __init__(self, name, uid, only):
        self.name = name
        self.uid = uid
        self.only = only

class Row(object):
    """docstring for Row"""
    def __init__(self, name, func):
        super(Row, self).__init__()
        self.name = name
        self.func = func
        

class AdminResource(object):
    actions = ('index', 'edit', 'show', 'delete', )
    filters = ('_id', )
    scopes = ()
    sidebars = ()
    
    index_columns = (
        Column('ID', '_id', sortable='_id', uid='_id'),
    )
    
    def __init__(self, model):
        """docstring for __init__"""
        self.model = model
        
        if isinstance(self.model, (str, unicode, basestring, )):
            _name = self.model.capitalize()
        else:
            _name = self.model.__name__
        
        self.name = _name.capitalize().replace('_', ' ').replace('-', ' ')
        self.slug = self.name.lower()
    
    def content_for_column(self, handler, column, obj=None):
        value = obj.get(column.field)
        if column.i18n and isinstance(value, dict):
            return value[handler.locale.lang]
            
        if column.uid == 'pk':
            return '<a href="%s">%s</a>' % (handler.reverse_url('admin:resource:detail:object', handler.resource.slug, obj[column.field]), value, )
        return value
        
    def content_for_sidebar(self, handler, sidebar, obj=None):
        """docstring for content_for_sidebar"""
        return 'Sidebar'
        
    # show_content = (
    #     panel('Invoice', uid='invoice')
    # )
    
    # show:
    #     - panels (name)
    #     - table_for(items) : columns(...), column, tr, td
    #     - attributes_table_for field/model, row
    #     
    #     sidebar (name), only:(show, index, edit):
    #     - render
    #     
    #     section (name)
    #  
    
class SiteAdmin(object):
    resources_by_model = {}
    resources_by_slug = {}
    _resources = []
    dashboard = None
    
    def register(self, model_name, Resource=AdminResource):
        """docstring for register"""
        if isinstance(model_name, (str, unicode, basestring, )):
            # for model_name2, model2 in loading.cache.models.items():
                # print model_name2, model2
            model = loading.get_model(model_name)
            if model is None:
                raise Exception('Model %s doesnt exist' % (model_name, ))
        else:
            model = model_name

        if model in self.resources_by_model:
            raise Exception('Aldready registered')
        
        resource = Resource(model)
        self.resources_by_model[model] = resource
        self.resources_by_slug[resource.slug] = resource
        self._resources.append(resource)
        
    def unregister(self, model):
        """docstring for unregister"""
        if model in self.resources_by_model:
            resource = self.resources_by_model[model]
            del self.resources_by_slug[resource.slug]
            del self.resources_by_model[model]
        
    def set_dashboard(self, dashboard):
        """docstring for set_dashboard"""
        self.dashboard = dashboard
        
    def get_resource(self, slug):
        """docstring for get_resource"""
        return self.resources_by_slug.get(slug)

    @property
    def resources(self):
        """docstring for resources"""
        return self._resources
    
    
site = SiteAdmin()