#!/usr/bin/env python
# -*- coding: utf-8 -*-
# encoding: utf-8
"""
validations.py

Created by Olivier Hardy on 2011-11-22.
Copyright (c) 2011 Olivier Hardy. All rights reserved.
"""

import re

email_re = re.compile(
    r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*"  # dot-atom
    r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-011\013\014\016-\177])*"' # quoted-string
    r')@(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?$', re.IGNORECASE)  # domain

url_re = re.compile(
    r'^https?://' # http:// or https://
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|' #domain...
    r'localhost|' #localhost...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
    r'(?::\d+)?' # optional port
    r'(?:/?|[/?]\S+)$', re.IGNORECASE)

def is_valid_email(email):
    """docstring for check_email"""
    return email is not None and email_re.match(email) is not None

def is_valid_url(url):
    """docstring for fname"""
    return url is not None and url_re.match(url) is not None