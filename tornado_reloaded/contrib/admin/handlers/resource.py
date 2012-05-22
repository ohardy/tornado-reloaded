# -*- coding: utf-8 -*-
# encoding: utf-8
"""
__init__.py

Created by Olivier Hardy on 2012-04-17.
Copyright (c) 2012 Olivier Hardy. All rights reserved.
"""

import tornado.web
from tornado import gen

from base import BaseHandler

from tornado_reloaded.contrib.admin.resources import site
from tornado_reloaded.web import is_superuser

class ActiveHandler:
    active_menu_item = 'resource'

class ResourceDetailHandler(ActiveHandler, BaseHandler):
    action = 'index'
    @is_superuser
    @tornado.web.asynchronous
    @gen.engine
    def get(self, resource):
        self.resource = site.get_resource(resource)
        Document = self.get_document_class(self.resource.model)
        objects = yield gen.Task(Document.all())

        self.render('resource/index.html', objects=objects)

class ResourceObjectShowHandler(ActiveHandler, BaseHandler):
    action = 'show'
    @is_superuser
    @tornado.web.asynchronous
    @gen.engine
    def get(self, resource, pk):
        self.resource = site.get_resource(resource)
        Document = self.get_document_class(self.resource.model)
        obj = yield gen.Task(Document.find(pk))

        self.render('resource/object_show.html', obj=obj)
