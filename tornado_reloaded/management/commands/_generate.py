#!/usr/bin/env python
# -*- coding: utf-8 -*-
# encoding: utf-8
"""
generate.py

Created by Olivier Hardy on 2011-10-10.
Copyright (c) 2011 Olivier Hardy. All rights reserved.
"""

from tornado_reloaded.management import Command

class GenerateCommand(Command):
    """docstring for GenerateCommand"""
    name = 'generate'
    
    def handle(self):
        """docstring for handle"""
        print 'handle'
