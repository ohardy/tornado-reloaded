#!/usr/bin/env python
# -*- coding: utf-8 -*-
# encoding: utf-8
"""
user.py

Created by Olivier Hardy on 2011-12-01.
Copyright (c) 2011 Olivier Hardy. All rights reserved.
"""

import tornado.web

from tornado_reloaded.web import RequestHandler

class UserHandler(RequestHandler):
    active_menu_item = 'user:current'
    
    @tornado.web.asynchronous
    def get(self, username):
        self.db.users.find_one({
                'username': username
            }, fields = {
                'password': 0
            }, callback=self._on_response)
    
    def _on_response(self, response):
        self.render('user/detail.html', user=response)