#!/usr/bin/env python
# -*- coding: utf-8 -*-
# encoding: utf-8
"""
new.py

Created by Olivier Hardy on 2012-01-11.
Copyright (c) 2011 Olivier Hardy. All rights reserved.
"""

import os
from datetime import datetime

from skeleton import Skeleton, Var

from tornado_reloaded.management import Command
from tornado_reloaded.utils import gen_cookie_secret

from ..init import BasicModule

class NewCommand(Command):
    """docstring for ServerCommand"""
    name        = 'new'
    
    # def add_arguments(self, subparser):
    #         """docstring for add_argumentd"""
    #         subparser.add_argument('folder', nargs='?')
    
    def handle(self, folder):
        """docstring for handle"""
        if folder is None:
            raise Exception('Project path is required')
        basic_module = BasicModule()
        basic_module['cookie_secret'] = gen_cookie_secret()
        basic_module['today'] = datetime.now().strftime('%Y-%m-%d')
        basic_module.run(os.path.abspath(folder))
