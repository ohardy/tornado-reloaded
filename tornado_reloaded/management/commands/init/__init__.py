#!/usr/bin/env python
# -*- coding: utf-8 -*-
# encoding: utf-8
"""
init.py

Created by Olivier Hardy on 2012-01-06.
Copyright (c) 2011 Olivier Hardy. All rights reserved.
"""

import os
from datetime import datetime

from skeleton import Skeleton, Var

from tornado_reloaded.management import Command
from tornado_reloaded.utils import gen_cookie_secret

class BasicModule(Skeleton):
    src = 'skeleton'
    variables = [
        Var('Project Name'),
        Var('Author Name'),
        Var('Database name'),
        Var('Domain splitted'),
        # Var('Author Email'),
        Var('Cookie secret'),
        Var('today')
    ]

class InitCommand(Command):
    """docstring for ServerCommand"""
    name        = 'init'
    
    def handle(self):
        """docstring for handle"""
        basic_module = BasicModule()
        basic_module['Cookie secret'] = gen_cookie_secret()
        basic_module['today'] = datetime.now().strftime('%Y-%m-%d')
        basic_module.run(os.getcwd())
