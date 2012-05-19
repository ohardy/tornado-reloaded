#!/usr/bin/env python
# -*- coding: utf-8 -*-
# encoding: utf-8
"""
base.py

Created by Olivier Hardy on 2011-10-10.
Copyright (c) 2011 Olivier Hardy. All rights reserved.
"""

import sys
import re
import argparse
from itertools import izip
from bisect import bisect

from loading import get_command
from loading import register_command

class CommandBase(type):
    def __new__(cls, name, bases, attrs):
        """docstring for __new__"""
        
        super_new = super(CommandBase, cls).__new__
        parents = [b for b in bases if isinstance(b, CommandBase)]
        if not parents:
            return super_new(cls, name, bases, attrs)
        
        # module    = attrs.pop('__module__')
        try:
            name      = attrs.pop('name')
        except KeyError:
            raise Exception('name class attribute is required')
        
        new_class = super_new(cls, name, bases, attrs)
        
        return register_command(name, new_class)

class Command(object):
    __metaclass__ = CommandBase
    
    require_env = False
    options     = []
    help        = None
    aliases     = []
    async       = False
    
    def __init__(self):
        """docstring for __init__"""
        pass
    
    def get_options(self):
        """docstring for get_options"""
        return self.options
    
    def get_parser(self):
        """docstring for get_root_parser"""
        return argparse.ArgumentParser(prog='PROG')
    
    def get_help(self):
        """docstring for get_help"""
        return self.help
    
    def _add_arguments(self, management_utility, subparser):
        """docstring for add_arguments"""
        if self.require_env:
            subparser.add_argument('env', choices=management_utility.get_envs())
        
        self.add_arguments(subparser)
    
    def add_arguments(self, subparser):
        """docstring for add_arguments"""
        pass
    
    def get_aliases(self):
        """docstring for get_aliases"""
        return self.aliases
