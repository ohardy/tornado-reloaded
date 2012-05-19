#!/usr/bin/env python
# -*- coding: utf-8 -*-
# encoding: utf-8

import handlers

from tornado import gen

class SitemapEntry(object):
    """docstring for SitemapEntry"""
    def __init__(self, sitemap, handler, item):
        super(SitemapEntry, self).__init__()
        self.sitemap = sitemap
        self.handler = handler
        self.item    = item
    
    def _result_or_none(self, result):
        """docstring for _result_or_none"""
        if result is NotImplemented:
            return None
        
        return result
    
    def location(self):
        """docstring for location"""
        return self.sitemap.location(self.handler, self.item)
    
    def last_modified(self):
        """docstring for last_modified"""
        return self._result_or_none(self.sitemap.last_modified(self.handler, self.item))
    
    def change_frequency(self):
        """docstring for change_frequency"""
        return self._result_or_none(self.sitemap.change_frequency(self.handler, self.item))
    
    def priority(self):
        """docstring for priority"""
        return self._result_or_none(self.sitemap.priority(self.handler, self.item))
    
    def is_ssl(self):
        """docstring for is_ssl"""
        return self.sitemap.is_ssl(self.handler, self.item)
    
    def description(self):
        """docstring for is_ssl"""
        return self._result_or_none(self.sitemap.description(self.handler, self.item))

class Sitemap(object):
    """docstring for Sitemap"""
    ALWAYS  = 'always'
    HOURLY  = 'hourly'
    DAILY   = 'daily'
    WEEKLY  = 'weekly'
    MONTHLY = 'monthly'
    YEARLY  = 'yearly'
    NEVER   = 'never'
    
    def __init__(self, limit=50000):
        super(Sitemap, self).__init__()
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
        
        if not isinstance(response, (list, tuple, )):
            response = [response]
        
        for item in response:
            items.append(SitemapEntry(self, handler, item))
        
        callback(items)
    
    def items(self, handler, callback):
        """docstring for items"""
        return []
    
    def location(self, handler, obj):
        """docstring for location"""
        raise NotImplementedError()
    
    def last_modified(self, handler, obj):
        """docstring for last_modified"""
        return NotImplemented
    
    def change_frequency(self, handler, obj):
        """docstring for change_frequency"""
        return NotImplemented
    
    def priority(self, handler, obj):
        """docstring for priority"""
        return NotImplemented
    
    def description(self, handler, obj):
        """docstring for priority"""
        return NotImplemented

class Sitemaps(object):
    """docstring for Sitemaps"""
    def __init__(self):
        super(Sitemaps, self).__init__()
        self.sitemaps = []
    
    def __iter__(self):
        """docstring for __iter__"""
        return iter(self.sitemaps)
    
    def add(self, sitemap):
        """docstring for add"""
        self.sitemaps.append(sitemap)
    
    @gen.engine
    def get_items(self, handler, callback):
        """docstring for get_items"""
        items = []
        
        for sitemap in self.sitemaps:
            response = yield gen.Task(sitemap.get_items, handler)
            items.extend(response)
        
        callback(items)