# -*- coding: utf-8 -*-
# encoding: utf-8
"""
__init__.py

Created by Olivier Hardy on 2012-04-17.
Copyright (c) 2012 Olivier Hardy. All rights reserved.
"""
import os
# import copy

import tornado.web
from tornado import gen

from tornado_reloaded.web import RequestHandler
from tornado_reloaded.contrib.admin.modules import HeaderModule
from tornado_reloaded.contrib.admin.modules import PartialModule

class BaseHandler(RequestHandler):
    def __init__(self, application, request, spec_match, url_lang=None, **kwargs):
        application.ui_modules['HeaderModule'] = HeaderModule
        application.ui_modules['PartialModule'] = PartialModule
        super(RequestHandler, self).__init__(application, request, spec_match, url_lang, **kwargs)
        self.resource = None
        
    @property
    def settings(self):
        """An alias for `self.application.settings`."""
        if not hasattr(self, '_settings'):
            self._settings = {}
            for name, value in self.application.settings.items():
                self._settings[name] = value
            # self._settings = copy.deepcopy(self.application.settings)
            self._settings['template_path']         = os.path.join(os.path.dirname(__file__), '../templates/')
            self._settings['static_path']         = os.path.join(os.path.dirname(__file__), '../static/')
            self._settings['static_url_prefix']   = '/admin_static/'
        return self._settings