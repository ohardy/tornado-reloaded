#!/usr/bin/env python
# -*- coding: utf-8 -*-
# encoding: utf-8
"""
handlers.py

Created by Olivier Hardy on 2012-01-03.
Copyright (c) 2011 Olivier Hardy. All rights reserved.
"""

import os.path
import functools

import tornado
from tornado_reloaded.auth import AnonymousUser
from tornado_reloaded.web import RequestHandler

class FeedHandler(RequestHandler):
    """A simple handler that can serve feed.
    
    To map a feed, you would add a line to your application like:
        
        feeds = Feeds()
        feeds.add('blog.xml', ArticleSitemap())
        
        application = web.Application([
            (r"/blog.xml", tornado_reloaded.feed.handlers.FeedHandler, {"feeds" : feeds, "name": "blog.xml"}),
        ])
    
    """
    def initialize(self, feeds, name):
        self.feeds = feeds
        self.name = name
    
    def before_prepare(self, method, *args, **kwargs):
        """docstring for before_prepare"""
        method = functools.partial(self.after_prepare, method, *args, **kwargs)
        
        self._current_user = AnonymousUser()
        self.prepare(method)
    
    @tornado.web.asynchronous
    def get(self):
        self.feeds.get_items(self, self.name, self.on_get_items)
    
    def on_get_items(self, feed, items):
        """docstring for on_get_items"""
        kwargs = {
        
        }
        
        kwargs['items'] = items
        kwargs['title'] = feed.title(self)
        kwargs['description'] = feed.description(self)
        kwargs['link'] = feed.link(self)
        kwargs['pub_date'] = feed.pub_date(self)
        kwargs['last_build_date'] = feed.last_build_date(self)
        kwargs['image'] = feed.image(self)
        kwargs['language'] = feed.language(self)
        
        path = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates'))
        self.set_header("Content-Type", "application/rss+xml")
        self.render(u"%s/rss.xml" % (path, ), **kwargs)
