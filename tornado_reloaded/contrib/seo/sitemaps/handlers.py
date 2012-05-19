#!/usr/bin/env python
# -*- coding: utf-8 -*-
# encoding: utf-8

import os.path
import functools

import tornado
from tornado_reloaded.auth import AnonymousUser
from tornado_reloaded.web import RequestHandler

class SitemapHandler(RequestHandler):
    """A simple handler that can serve sitemaps.
    
    To map a sitemap, you would add a line to your application like:
        
        sitemaps = Sitemaps()
        sitemaps.add(ArticleSitemap())
        
        application = web.Application([
            (r"/sitemap.xml", tornado_reloaded.sitemaps.handlers.SitemapHandler, {"sitemaps": sitemaps}),
        ])
    """
    def initialize(self, sitemaps):
        self.sitemaps = sitemaps
    
    def before_prepare(self, method, *args, **kwargs):
        """docstring for before_prepare"""
        method = functools.partial(self.after_prepare, method, *args, **kwargs)
        
        self._current_user = AnonymousUser()
        self.prepare(method)
    
    @tornado.web.asynchronous
    def get(self):
        self.sitemaps.get_items(self, self.on_get_items)
    
    def on_get_items(self, items):
        """docstring for on_get_items"""
        path = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates'))
        self.set_header("Content-Type", "text/xml")
        self.render(u"%s/sitemap.xml" % (path, ), items=items)