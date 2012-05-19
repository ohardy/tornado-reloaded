#!/usr/bin/env python
# -*- coding: utf-8 -*-
# encoding: utf-8
"""
decorators.py

Created by Olivier Hardy on 2011-11-21.
Copyright (c) 2011 Olivier Hardy. All rights reserved.
"""

import urllib
import urlparse
import functools

from tornado.web import HTTPError

def is_staff(redirect=False):
    """Decorate methods with this to require that the user be logged in."""
    def _is_staff(method):
        @functools.wraps(method)
        def wrapper(self, redirect=False, *args, **kwargs):
            if not self.current_user or not self.current_user.is_staff:
                if redirect:
                    if self.request.method in ("GET", "HEAD"):
                        url = self.get_login_url()
                        if "?" not in url:
                            if urlparse.urlsplit(url).scheme:
                                # if login url is absolute, make next absolute too
                                next_url = self.request.full_url()
                            else:
                                next_url = self.request.uri
                            url += "?" + urllib.urlencode(dict(next=next_url))
                        self.redirect(url)
                        return
                raise HTTPError(403)
            return method(self, *args, **kwargs)
        return wrapper
    return _is_staff