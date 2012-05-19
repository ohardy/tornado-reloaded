#!/usr/bin/env python
# -*- coding: utf-8 -*-
# encoding: utf-8
"""
loading.py

Created by Olivier Hardy on 2011-10-10.
Copyright (c) 2011 Olivier Hardy. All rights reserved.
"""

commands = {}

def get_command(name):
    """docstring for get_command"""
    return commands[name]

def register_command(name, command):
    """docstring for register_command"""
    if not name in commands:
        commands[name] = command
    else:
        raise Exception('A command already exists with name : %s' % (name, ))
    return commands[name]

def get_commands():
    """docstring for get_commands"""
    return commands
