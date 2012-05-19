#!/usr/bin/env python
# -*- coding: utf-8 -*-
# encoding: utf-8
"""
applications.py

Created by Olivier Hardy on 2011-11-22.
Copyright (c) 2011 Olivier Hardy. All rights reserved.
"""

import logging
from threading import Condition

import tornado.web
from tornado.options import define
from tornado.options import options
from tornado import locale

from db import get_db

define("absolute_base_url", type                 = str,      default=None,              multiple=False)
define("static_handler_class", type              = object,      default=None,              multiple=False)
define("listen",            type                 = str,      default=[],                multiple=True)
define("methods",           type                 = str,      default=[],                multiple=True)
define("modules",           type                 = str,      default=[],                multiple=True)
define("handlers",          type                 = str,      default=[],                multiple=True)
define("tasks",             type                 = str,      default=[],                multiple=True)
define("scheduled_tasks",   type                 = dict,     default={})
define("nb",                type                 = int,      default=0)
define("title",             type                 = unicode)
define("default_host",      type                 = str)
define("cookie_secret",     type                 = unicode)
define("debug",             type                 = bool)
define("databases",         type                 = dict,      default={})
define("caches",            type                 = dict,      default={})
define("env",          	    help                 = "run on the given environnement",      type=unicode)
define("server_name",       help                 = "run on the given environnement",      type=str)
define("registration_require_invitation",   type = bool,      default=False)
define("invitation_enabled",                type = bool,      default=False)
define("user_properties",   type=str, default=[], multiple=True)

class Application(tornado.web.Application):
    """docstring for Application"""
    def __init__(self, handlers=None, default_host="", transforms=None,
                 wsgi=False, **settings):
        
        if options.static_handler_class:
            settings['static_handler_class'] = options.static_handler_class
        super(Application, self).__init__(handlers, default_host, transforms, wsgi, **settings)
        
        self._condition = Condition()
        self._db        = None
    
    @property
    def db(self):
        """Return a db instance if databases option is defined"""
        self._condition.acquire()
        if not hasattr(self, '_db') or self._db is None:
            self._db = get_db()
        
        return self._db
    
    @property
    def cache(self):
        """Return a cache instance if caches option is defined"""
        if hasattr(self, '_cache') and self._cache is not None:
            return self._cache
        
        self._condition.acquire()
        try:
            if options.caches.get('default', False) and options.caches['default']['backend'] == 'redis':
                import brukva
                self._cache = brukva.Client()
                self._cache.connect()
        finally:
            self._condition.release()
        
        return self._cache
