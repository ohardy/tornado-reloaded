#!/usr/bin/env python
# -*- coding: utf-8 -*-
# encoding: utf-8
"""
server.py

Created by Olivier Hardy on 2011-10-10.
Copyright (c) 2011 Olivier Hardy. All rights reserved.
"""

from tornado_reloaded.management import Command

from tornado_reloaded.servers import runserver

class RunserverCommand(Command):
    """docstring for ServerCommand"""
    name        = 'runserver'
    require_env = True
    
    def handle(self):
        """docstring for handle"""
        runserver()
