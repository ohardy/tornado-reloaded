#!/usr/bin/env python
# -*- coding: utf-8 -*-
# encoding: utf-8
"""
server.py

Created by Olivier Hardy on 2011-12-22.
Copyright (c) 2011 Olivier Hardy. All rights reserved.
"""

import os
from functools import partial

import tornado.options
import tornado.locale
import tornado.httpserver
import tornado.ioloop

from tornado.options import options

import tornado_reloaded.methods as tornado_reloaded_methods
import tornado_reloaded.modules as tornado_reloaded_modules
from applications import Application

from tornado_reloaded.utils import get_module_from_import

def runserver(*args, **kwargs):
    """docstring for runserver"""
    current_dir = os.getcwd()
    
    try:
        locale_folder = os.path.join(current_dir, 'locale')
        if os.path.exists(locale_folder):
            tornado.locale.load_gettext_translations(locale_folder, 'tornado')
        
        handlers = []
        for handler_module_name in options.handlers:
            handler_list = get_module_from_import(handler_module_name)
            handlers.extend(handler_list)
        
        methods = []
        for methods_module_name in options.methods:
            methods_module = get_module_from_import(methods_module_name)
            methods.append(methods_module)
        
        modules = []
        for modules_module_name in options.modules:
            modules_module = get_module_from_import(modules_module_name)
            modules.append(modules_module)
        
        methods.insert(0, tornado_reloaded_methods)
        modules.insert(0, tornado_reloaded_modules)
        
        application = Application(
            handlers      = handlers,
            default_host  = options.default_host,
            debug         = options.debug,
            cookie_secret = options.cookie_secret,
            template_path = os.path.join(current_dir, "templates"),
            static_path   = os.path.join(current_dir, "static"),
            title         = options.title,
            ui_methods    = methods,
            ui_modules    = modules,
            # transforms  = [transforms.HighlightCode],
            env           = options.env,
            *args,
            **kwargs
        )
        http_server = tornado.httpserver.HTTPServer(application, xheaders=True)

        if not options.listen:
            raise Exception('listen parameter is required')
        
        for listen in set(options.listen):
            port    = None
            address = None
            
            if isinstance(listen, int):
                port = listen
            elif isinstance(listen, basestring):
                if ':' in listen:
                    elts = listen.split(':')
                    address = elts[0]
                    port = elts[1]
                else:
                    port = int(listen)
            
            http_server.bind(port, address=address)
        
        http_server.start(options.nb)
        
        ioloop = tornado.ioloop.IOLoop.instance()
        
        ioloop.start()
    except KeyboardInterrupt:
        pass
