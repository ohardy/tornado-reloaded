#!/usr/bin/env python
# -*- coding: utf-8 -*-
# encoding: utf-8
"""
__init__.py

Created by Olivier Hardy on 2011-10-10.
Copyright (c) 2011 Olivier Hardy. All rights reserved.
"""

import runserver
import init
import makemessages
import compilemessages
import new
# import generate

import pkg_resources

for ep in pkg_resources.iter_entry_points('tornado_reloaded.management.commands'):
    ep.load()
