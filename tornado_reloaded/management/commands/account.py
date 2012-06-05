#!/usr/bin/env python
# -*- coding: utf-8 -*-
# encoding: utf-8
"""
server.py

Created by Olivier Hardy on 2012-05-30.
Copyright (c) 2012 Olivier Hardy. All rights reserved.
"""

import getpass
import sys
import hashlib
from datetime import datetime

from tornado import gen

from tornado_reloaded.management import Command
from tornado_reloaded.db import get_db
from tornado_reloaded.servers import runserver
from tornado_reloaded.utils import get_random_string

method = 'sha512'

class AccountPasswordCommand(Command):
    """docstring for ServerCommand"""
    name        = 'account:passwd'
    require_env = True
    
    def add_arguments(self, subparser):
        subparser.add_argument('username')
    
    def _get_pass(self, prompt="Password: "):
        p = getpass.getpass(prompt=prompt)
        if not p:
            raise Exception("aborted")
        return p
    
    @gen.engine
    def handle(self, username):
        MAX_TRIES = 3
        count = 0
        p1, p2 = 1, 2  # To make them initially mismatch.
        while p1 != p2 and count < MAX_TRIES:
            p1 = self._get_pass()
            p2 = self._get_pass("Password (again): ")
            if p1 != p2:
                sys.stdout.write("Passwords do not match. Please try again.\n")
                count = count + 1

        if count == MAX_TRIES:
            raise Exception("Aborting password change for user '%s' after %s attempts" % (username, count))
        
        print p1, p2
        if p1 == p2:
            print 'HERE'
            self.db = get_db()
            
            p        = getattr(hashlib, method)()
            salt     = get_random_string()
            p.update("%s%s" % (salt, p1, ))
            password = p.hexdigest()
            
            print 'BEFORE'
            
            response = yield gen.Task(self.db.users.update, {
                'username': username
            }, {
                '$set' : {
                    'password' : {
                        'hash'      : password,
                        'method'    : method,
                        'salt'      : salt
                    },
                    'modification_date' : datetime.utcnow()
                }
            })
            
            print 'RES : ', response
