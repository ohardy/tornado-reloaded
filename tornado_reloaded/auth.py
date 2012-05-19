#!/usr/bin/env python
# -*- coding: utf-8 -*-
# encoding: utf-8
"""
auth.py

Created by Olivier Hardy on 2011-11-21.
Copyright (c) 2011 Olivier Hardy. All rights reserved.
"""

class User(object):
    """docstring for User"""
    def __init__(self, email=None, username=None, id=None, is_superuser=False, is_staff=False, can_invite=False, **kwargs):
        super(User, self).__init__()
        self.email        = email
        self.username     = username
        self.id           = id
        self.is_superuser = is_superuser
        self.is_staff     = is_staff
        self.can_invite   = (self.is_staff or self.is_superuser) and True or can_invite
        self.kwargs       = kwargs
    
    def __nonzero__(self):
        """docstring for __nonzero__"""
        return True
    
    def is_authenticated(self):
        """docstring for is_authenticated"""
        return True
    
    def __unicode__(self):
        """docstring for __unicode__"""
        return self.username or self.email or self.id or 'Unknown'
    
    def __str__(self):
        """docstring for __str__"""
        return unicode(self)
        
    def get(self, name, default=None):
        """docstring for get"""
        value = self.kwargs.get(name, default)
        if value is None:
            return default
        
        return value

class AnonymousUser(User):
    """docstring for AnonymousUser"""
    def __nonzero__(self):
        """docstring for __nonzero__"""
        return False
    
    def __unicode__(self):
        """docstring for __unicode__"""
        return 'Anonymous user'
    
    def is_authenticated(self):
        """docstring for is_authenticated"""
        return False
