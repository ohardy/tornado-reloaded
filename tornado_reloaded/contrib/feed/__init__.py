#!/usr/bin/env python
# -*- coding: utf-8 -*-
# encoding: utf-8
"""
__init__.py

Created by Olivier Hardy on 2012-01-03.
Copyright (c) 2011 Olivier Hardy. All rights reserved.
"""

import handlers

from tornado import gen

class FeedEntry(object):
    """docstring for SitemapEntry"""
    def __init__(self, feed, handler, item):
        super(FeedEntry, self).__init__()
        self.feed = feed
        self.handler = handler
        self.item    = item
    
    def _result_or_none(self, result):
        """docstring for _result_or_none"""
        if result is NotImplemented:
            return None
        
        return result
    
    def title(self):
        """docstring for location"""
        return self.feed.title(self.handler, self.item)
    
    def description(self):
        """docstring for last_modified"""
        return self.feed.description(self.handler, self.item)
    
    def link(self):
        """docstring for change_frequency"""
        return self.feed.link(self.handler, self.item)
    
    def pub_date(self):
        """docstring for priority"""
        return self._result_or_none(self.feed.pub_date(self.handler, self.item))
    
    def last_build_date(self):
        """docstring for is_ssl"""
        return self._result_or_none(self.feed.last_build_date(self.handler, self.item))
    
    def image(self):
        """docstring for is_ssl"""
        return self._result_or_none(self.feed.image(self.handler, self.item))
    
    def language(self):
        """docstring for is_ssl"""
        return self._result_or_none(self.feed.language(self.handler, self.item))
    
    def item_title(self):
        """docstring for is_ssl"""
        return self._result_or_none(self.feed.item_title(self.handler, self.item))
    
    def item_link(self):
        """docstring for is_ssl"""
        return self._result_or_none(self.feed.item_link(self.handler, self.item))
    
    def item_pub_date(self):
        """docstring for is_ssl"""
        return self._result_or_none(self.feed.item_pub_date(self.handler, self.item))
    
    def item_description(self):
        """docstring for is_ssl"""
        return self._result_or_none(self.feed.item_description(self.handler, self.item))
    
    def item_guid(self):
        """docstring for is_ssl"""
        return self._result_or_none(self.feed.item_guid(self.handler, self.item))
    
    def item_author(self):
        """docstring for is_ssl"""
        return self._result_or_none(self.feed.item_author(self.handler, self.item))
    
    def item_category(self):
        """docstring for is_ssl"""
        return self._result_or_none(self.feed.item_category(self.handler, self.item))
    
    def item_comments(self):
        """docstring for is_ssl"""
        return self._result_or_none(self.feed.item_comments(self.handler, self.item))
    
    def is_ssl(self):
        """docstring for is_ssl"""
        return self.feed.is_ssl(self.handler, self.item)

class Feed(object):
    """docstring for Sitemap"""
    def __init__(self, limit=50000):
        super(Feed, self).__init__()
        self.limit = limit
    
    def __iter__(self):
        """docstring for __iter__"""
        raise Exception('Use .get_items(handler)')
    
    def is_ssl(self):
        """docstring for is_ssl"""
        return NotImplemented
    
    @gen.engine
    def get_items(self, handler, callback):
        """docstring for get_items"""
        items = []
        
        response = yield gen.Task(self.items, handler)
        
        for item in response:
            items.append(FeedEntry(self, handler, item))
        
        callback(items)
    
    def items(self, handler, callback):
        """docstring for items"""
        return []
    
    def item_title(self, handler, obj):
        """docstring for location"""
        raise NotImplementedError()
    
    def item_link(self, handler, obj):
        """docstring for location"""
        return NotImplemented
    
    def item_pub_date(self, handler, obj):
        """docstring for location"""
        return NotImplemented
    
    def item_description(self, handler, obj):
        """docstring for location"""
        return NotImplemented
    
    def item_guid(self, handler, obj):
        """docstring for location"""
        return NotImplemented
    
    def item_author(self, handler, obj):
        """docstring for location"""
        return NotImplemented
    
    def item_category(self, handler, obj):
        """docstring for location"""
        return NotImplemented
    
    def item_comments(self, handler, obj):
        """docstring for location"""
        return NotImplemented
    
    def title(self, handler):
        """docstring for location"""
        raise NotImplementedError()
    
    def description(self, handler):
        """docstring for location"""
        raise NotImplementedError()
    
    def link(self, handler):
        """docstring for location"""
        raise NotImplementedError()
    
    def pub_date(self, handler):
        """docstring for location"""
        return None
    
    def last_build_date(self, handler):
        """docstring for location"""
        return None
    
    def image(self, handler):
        """docstring for location"""
        return None
    
    def language(self, handler):
        """docstring for location"""
        return None

class Feeds(object):
    """docstring for Sitemaps"""
    def __init__(self):
        super(Feeds, self).__init__()
        self.feeds = {}
    
    def __iter__(self):
        """docstring for __iter__"""
        return iter(self.feed)
    
    def add(self, name, feed):
        """docstring for add"""
        self.feeds[name] = feed
    
    @gen.engine
    def get_items(self, handler, name, callback):
        """docstring for get_items"""
        items = []
        
        response = yield gen.Task(self.feeds[name].get_items, handler)
        items.extend(response)
        
        callback(self.feeds[name], items)
