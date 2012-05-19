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

class ActiveHandler:
    active_menu_item = 'dashboard'

class IndexHandler(ActiveHandler, BaseHandler):
    # @tornado.web.asynchronous
    # @gen.engine
    def get(self):
        self.render('dashboard.html')
