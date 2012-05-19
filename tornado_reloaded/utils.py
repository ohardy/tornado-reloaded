#!/usr/bin/env python
# -*- coding: utf-8 -*-
# encoding: utf-8
"""
utils.py

Created by Olivier Hardy on 2011-11-17.
Copyright (c) 2011 Olivier Hardy. All rights reserved.
"""

import hashlib
import colorsys
import base64
import uuid
from datetime import datetime
from random import uniform

def _(to_translate):
    """docstring for _"""
    return to_translate

def get_module_from_import(name):
    """docstring for do_import"""
    components = name.split('.')
    mod = __import__(components[0])
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod

def get_python_date(date=None):
    """docstring for get_python"""
    if date:
        return date
    
    return datetime.utcnow()

def check_hash(password_hash, response):
    """docstring for check_hash"""
    return password_hash == response['password']['hash']

def get_user_from_auth(response, email, password):
    """docstring for get_user_from_auth"""
    if not response:
        raise Exception('No response')
    
    from auth import User
    from auth import AnonymousUser
    
    if email != response['email']:
        return AnonymousUser()
    
    p = getattr(hashlib, response['password']['method'])()
    p.update("%s%s" % (response['password']['salt'], password, ))
    password_hash = p.hexdigest()
    
    if not check_hash(password_hash, response):
        raise Exception('Invalid password')
    
    return User(
        email        = response['email'],
        username     = response['username'],
        id           = response['_id'],
        is_superuser = response.get('is_superuser', False),
        is_staff     = response.get('is_staff', False),
        can_invite   = response.get('can_invite', False)
    )

def check_auth(response, password, username=None, email=None):
    """docstring for check_auth"""
    
    if not response:
        return False
    
    if username is None and email is None:
        return False
    
    if username is not None and username != response.get('username'):
        return False
    
    if email is not None and email != response.get('email'):
        return False
    
    p = getattr(hashlib, response['password']['method'])()
    p.update("%s%s" % (response['password']['salt'], password, ))
    password_hash = p.hexdigest()
    
    if not check_hash(password_hash, response):
        return False
    
    return True

def do_auth(db, handler, password, method, username=None, email=None, callback=None):
    """docstring for do_auth"""
    def _on_find(response, error):
        """docstring for _on_find"""
        if check_auth(response, password, username=username, email=email):
            handler.set_secure_cookie("user",  response['username'])
            handler.set_secure_cookie("s_p",   response['password']['hash'])
    
    db.users.find({
        '$or': or_filters
    
    }, callback=_on_find)

def get_small_id(nb=None):
    unique_id = uuid.uuid4().int
    alphabet = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_-"
    encoded = ''
    while unique_id > 0:
        unique_id, r = divmod(unique_id, len(alphabet))
        encoded = alphabet[r] + encoded
    if nb:
        return encoded[0:nb]
    return encoded

def rgb_to_html_color(rgb):
    """Convert an (R, G, B) tuple to #RRGGBB"""
    return '#%02x%02x%02x' % rgb

def get_random_rgb_color():
    """docstring for get_random_rgb_color"""
    h = uniform(0.3, 1) # Select random green'ish hue from hue wheel
    s = uniform(0.2, 1)
    v = uniform(0.3, 1)
    
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    
    # Convert to 0-1 range for HTML output
    a = tuple([x*255 for x in (r, g, b)])
    
    return rgb_to_html_color(a)
    
    # Convert to 0-1 range for HTML output
    #
    #
    # a = (r, g, b, )
    #
    # # print "<span style='background:rgb(%i, %i, %i)'>&nbsp;&nbsp;</span>" % (r, g, b)
    # return rgb_to_html_color(a)

def get_random_string(length=12, allowed_chars='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'):
    """
    Returns a random string of length characters from the set of a-z, A-Z, 0-9
    for use as a salt.
    
    The default length of 12 with the a-z, A-Z, 0-9 character set returns
    a 71-bit salt. log_2((26+26+10)^12) =~ 71 bits
    """
    import random
    try:
        random = random.SystemRandom()
    except NotImplementedError:
        pass
    return ''.join([random.choice(allowed_chars) for i in range(length)])

def gen_cookie_secret():
    """docstring for gen_cookie_secret"""
    return base64.b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes)