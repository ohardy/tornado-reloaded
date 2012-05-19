#!/usr/bin/env python
# -*- coding: utf-8 -*-
# encoding: utf-8
"""
add_field_to.py

Created by Olivier Hardy on 2011-10-11.
Copyright (c) 2011 Olivier Hardy. All rights reserved.
"""

import os
import sys
import urlparse

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

from tornado.web import url

from tornado import admin

from tornado_reloaded.management import Command

from tornado.db.model.fields.loading import get_field_by_alias
from tornado.db.model.loading import get_model

class ServerCommand(Command):
    """docstring for ServerCommand"""
    name = 'add-field'
    
    # def add_arguments(self, subparser):
    #         subparser.add_argument('field')
    #         subparser.add_argument('to')
    
    def handle(self, field, to):
        """docstring for handle"""
        if not ':' in field:
            raise Exception('Field need type like : name:type')
        print get_field_by_alias(field.split(':')[1])
        print get_model(*to.split('.'))
