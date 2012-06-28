#!/usr/bin/env python
# -*- coding: utf-8 -*-
# encoding: utf-8
"""
web.py

Created by Olivier Hardy on 2012-05-16.
Copyright (c) 2011 Olivier Hardy. All rights reserved.
"""

import os
import sys
import mimetypes
import threading
import datetime
import stat
import hashlib
import functools
import logging
import email
import time

import tornado
from tornado.web import RequestHandler as OriginalRequestHandler
from tornado.web import StaticFileHandler as OriginalStaticFileHandler
from tornado.web import HTTPError

from tornado.ioloop import IOLoop
from tornado.options import options

from tornado_reloaded.utils import check_auth
from tornado_reloaded.utils import check_hash

from tornado_reloaded.auth import User
from tornado_reloaded.auth import AnonymousUser

from tornado_reloaded.handlers.static import call_subprocess

from tornado import gen
from tornado_reloaded.db.orm.documents import loading

try:
    from gprof2dot import gprof2dot
except:
    profile_enabled = False

class RequestHandler(OriginalRequestHandler):
    profile_enabled = False
    
    @property
    def db(self):
        return self.application.db
        
    def get_document_class(self, name):
        """docstring for get_collection"""
        if isinstance(name, (str, unicode, basestring, )):
            return loading.get_model(name)
        return name
        
    def write_error(self, status_code, **kwargs):
        """Override to implement custom error pages.
        
        ``write_error`` may call `write`, `render`, `set_header`, etc
        to produce output as usual.
        
        If this error was caused by an uncaught exception, an ``exc_info``
        triple will be available as ``kwargs["exc_info"]``.  Note that this
        exception may not be the "current" exception for purposes of
        methods like ``sys.exc_info()`` or ``traceback.format_exc``.
        
        For historical reasons, if a method ``get_error_html`` exists,
        it will be used instead of the default ``write_error`` implementation.
        ``get_error_html`` returned a string instead of producing output
        normally, and had different semantics for exception handling.
        Users of ``get_error_html`` are encouraged to convert their code
        to override ``write_error`` instead.
        """
        from error import _get_frames
        from error import _get_response_output
        from error import _get_response_headers
        from error import prettify
        from error import dicttable
        from error import dicttable_items
        import urlparse
        if status_code in (404, 400, 500, ):
            if 'exc_info' in kwargs:
                exc_info = kwargs['exc_info']
                logging.exception(exc_info[1])
                
            handler = self
            exception_type, exception_value, tback = exc_info
            is_debug = False
            #isinstance(exception_value, DebugBreakException)
    
            frames = _get_frames(tback, is_debug)
            frames.reverse()
    
            if is_debug:
                exception_type = 'Debug breakpoint'
                exception_value = ''
        
            urljoin = urlparse.urljoin
            import pprint
    
            params = {
                'exception_type': exception_type,
                'exception_value': exception_value,
                'frames': frames,
        
                'request_input': handler.request.body,
                'request_cookies': handler.cookies,
                'request_headers': handler.request.headers,
        
                'request_path': handler.request.uri,
                'request_method': handler.request.method,
                'response_output': _get_response_output(handler),
                'response_headers': _get_response_headers(handler),
        
                'dict': dict,
                'str': str,
                'prettify': prettify,
                'dicttable': dicttable,
                'dicttable_items': dicttable_items,
                'is_email': False,
                'pprint': pprint.pformat,
                'settings': self.application.settings,
                'sys_path': sys.path,
                'sys_executable': sys.executable,
                'sys_version': sys.version,
                'server_time': datetime.datetime.now(),
                'tornado_version': tornado.version,
                'lastframe': frames[-1],
            }
            kwargs.update(params)
            
                
            # try:
                # raise Exception()
                # self.render('%d.html' % (status_code, ), status_code=status_code, **kwargs)
            # except Exception as ef:
                # print 'EF : ', ef
                # try:
            self.render(os.path.join(os.path.dirname(__file__), 'templates/errors/technical.html'), status_code=status_code, **kwargs)
                # except Exception as e:
                    # print 'E : ', e
        else:
            super(RequestHandler, self).write_error(status_code, **kwargs)
    
    def before_initialize(self, **kwargs):
        """docstring for initialize"""
        if self.profile_enabled and profile_enabled:
            try:
                import cProfile as profile
            except ImportError:
                import profile
            
            self._prof = profile.Profile()
    
    def before_finish(self):
        """docstring for before_finish"""
        if self.profile_enabled and profile_enabled and hasattr(self._prof):
            self._prof.create_stats()
            parser = gprof2dot.PstatsParser(self._prof)
            
            def get_function_name((filename, line, name)):
                module = os.path.splitext(filename)[0]
                module_pieces = module.split(os.path.sep)
                return "%s:%d:%s" % ("/".join(module_pieces[-4:]), line, name)
            
            parser.get_function_name = get_function_name
            
            output = StringIO()
            gprof = parser.parse()
            
            gprof.prune(0.005, 0.001)
                    # TODO: ^--- Parameterize node and edge thresholds.
            dot = gprof2dot.DotWriter(output)
            theme = gprof2dot.TEMPERATURE_COLORMAP
            theme.bgcolor = (0.0, 0.0, 0.0)
                            # ^--- Use black text, for less eye-bleeding.
            dot.graph(gprof, theme)
            
            def get_info(self):
                s = "Profile Graph:"
                s += " %.3fs CPU" % self.total_tt
                s += ": %d function calls" % self.total_calls
                if self.total_calls != self.prim_calls:
                    s += " (%d primitive calls)" % self.prim_calls
                return s
            
            profile = {
              "producer": "gprof2dot",
              "producerVersion": str(gprof2dot.__version__),
              "info": get_info(parser.stats),
              "dot": output.getvalue(),
            }
            
            f = open('/tmp/tututu.dot', 'w')
            f.write(profile['dot'])
            f.close()
            
            # print profile
            
    # def _prepare(self, *args, **kwargs):
    #     self.prepare()
    #     if not self._finished:
    #         args = [self.decode_argument(arg) for arg in args]
    #         kwargs = dict((k, self.decode_argument(v, name=k))
    #                       for (k,v) in kwargs.iteritems())
    #         getattr(self, self.request.method.lower())(*args, **kwargs)
    #         if self._auto_finish and not self._finished:
    #             self.finish()
    
    def get_current_user(self):
        return getattr(self, '_current_user_object', None)
        
    def call_wrapper(method):
            """docstring for call_wrapper"""
            def wrapper(self, *args, **kwargs):
                """docstring for wrapper"""
                if self.profile_enabled:
                    return self._prof.runcall(method, self, *args, **kwargs)
                
                return method(self, *args, **kwargs)
        
            return wrapper
    
    if profile_enabled:
        _execute = call_wrapper(_execute)
            
    def prepare(self, callback):
        """docstring for prepare"""
        callback()
    
    @gen.engine
    def _prepare(self, *args, **kwargs):
        """docstring for before_prepare"""
        _ = yield gen.Task(self._load_current_user)
        _ = yield gen.Task(self.prepare)
        
        if not self._finished:
            args, kwargs = self._decode_args_and_kwargs(*args, **kwargs)
            method = self.request.method.lower()
            if isinstance(method, basestring):
                method = getattr(self.__class__, method)
            
            if not method.__self__:
                method = functools.partial(method, self)

            try:
                method(*args, **kwargs)
            except Exception as e:
                self._handle_request_exception(e)
            
            if self._auto_finish and not self._finished:
                self.finish()
    
    @gen.engine
    def _load_current_user(self, callback):
        """docstring for _load_current_user"""
        if self.current_user is None and self.application.settings.get('cookie_secret') and self.get_secure_cookie('email'):
            self._current_user = yield gen.Task(self.load_current_user)
        else:
            self._current_user = AnonymousUser()
        
        callback()
    
    @gen.engine
    def load_current_user(self, callback):
        """docstring for get_current_user"""
        email           = self.get_secure_cookie('email')
        password_hash   = self.get_secure_cookie('p_hash')
        
        #Use user_properties for fields arg
        response = yield gen.Task(self.db.users.find_one, {
                    'email' : email
                })
        
        if response:
            if check_hash(password_hash, response):
                def mod_callback3(insert_response):
                    """docstring for mod_callback"""
                    kwargs = {}
                    for name in options.user_properties:
                        kwargs[name] = response.get(name)
                    callback(User(
                        email             = response['email'],
                        username          = response['username'],
                        id                = response['_id'],
                        is_superuser      = response.get('is_superuser', False),
                        is_staff          = response.get('is_staff', False),
                        **kwargs
                    ))              
                self.db.users.update({
                        "_id": response['_id']
                    }, {
                        '$set' : {
                            'lastActivity': datetime.datetime.utcnow()
                        }
                    },
                    callback=mod_callback3
                )
                return

        self.clear_all_cookies()
        callback(AnonymousUser())
        
class ErrorHandler(RequestHandler):
    """docstring for ErrorHandler"""
    def initialize(self, status_code):
        self.set_status(status_code)

    def prepare(self, callback):
        if self.settings.get('debug', False):
            self.render(os.path.join(os.path.dirname(__file__), 'templates/errors/404.html'))
            callback()
            # self.render('%s.html' % (self._status_code, ), handlers=self.application.handlers)
        else:
            raise HTTPError(self._status_code)
        

class StaticFileHandler(OriginalStaticFileHandler):
    """A simple handler that can serve static content from a directory.
    
    To map a path to this handler for a static data directory /var/www,
    you would add a line to your application like::
        
        application = web.Application([
            (r"/static/(.*)", web.StaticFileHandler, {"path": "/var/www"}),
        ])
    
    The local root directory of the content should be passed as the "path"
    argument to the handler.
    
    To support aggressive browser caching, if the argument "v" is given
    with the path, we set an infinite HTTP expiration header. So, if you
    want browsers to cache a file indefinitely, send them to, e.g.,
    /static/images/myimage.png?v=xxx. Override ``get_cache_time`` method for
    more fine-grained cache control.
    """
    CACHE_MAX_AGE = 86400 * 365 * 10  # 10 years

    _static_hashes = {}
    _lock = threading.Lock()  # protects _static_hashes
    
    def initialize(self, path, default_filename=None):
        self.root = os.path.abspath(path) + os.path.sep
        self.default_filename = default_filename
    
    @classmethod
    def reset(cls):
        with cls._lock:
            cls._static_hashes = {}
    
    def head(self, path):
        self.get(path, include_body=False)
        
    @classmethod
    def abspath(cls, path):
        """docstring for abspath"""
        absfilename, absext = os.path.splitext(path)
        if absext == '.css' and not os.path.exists(path):
            return '%s%s' % (absfilename, '.scss', )
        
        return path
    
    @tornado.web.asynchronous
    @gen.engine
    def get(self, path, include_body=True):
        use_sass = False
        path = self.parse_url_path(path)
        abspath = os.path.abspath(os.path.join(self.root, path))
        # os.path.abspath strips a trailing /
        # it needs to be temporarily added back for requests to root/
        if not (abspath + os.path.sep).startswith(self.root):
            raise tornado.web.HTTPError(403, "%s is not in root static directory", path)
        if os.path.isdir(abspath) and self.default_filename is not None:
            # need to look at the request.path here for when path is empty
            # but there is some prefix to the path that was already
            # trimmed by the routing
            if not self.request.path.endswith("/"):
                self.redirect(self.request.path + "/")
                return
            abspath = os.path.join(abspath, self.default_filename)
        
        mime_type, encoding = mimetypes.guess_type(abspath)
        abspath2 = self.__class__.abspath(abspath)
        
        if abspath != abspath2:
            use_sass = True
            
        abspath = abspath2
            
        if not os.path.exists(abspath):
            raise tornado.web.HTTPError(404)
        if not os.path.isfile(abspath):
            raise tornado.web.HTTPError(403, "%s is not a file", path)
        
        stat_result = os.stat(abspath)
        modified = datetime.datetime.fromtimestamp(stat_result[stat.ST_MTIME])
        
        self.set_header("Last-Modified", modified)
        
        if mime_type:
            self.set_header("Content-Type", mime_type)
        
        cache_time = self.get_cache_time(path, modified, mime_type)
        
        if cache_time > 0:
            self.set_header("Expires", datetime.datetime.utcnow() + \
                                       datetime.timedelta(seconds=cache_time))
            self.set_header("Cache-Control", "max-age=" + str(cache_time))
        else:
            self.set_header("Cache-Control", "public")
        
        self.set_extra_headers(path)
        
        # Check the If-Modified-Since, and don't send the result if the
        # content has not been modified
        ims_value = self.request.headers.get("If-Modified-Since")
        if ims_value is not None:
            date_tuple = email.utils.parsedate(ims_value)
            if_since = datetime.datetime.fromtimestamp(time.mktime(date_tuple))
            if if_since >= modified:
                self.set_status(304)
        else:
            if use_sass:
                response = yield gen.Task(call_subprocess, self, str("sass %s" % (abspath, )))
                self.write(response.read())
            else:
                with open(abspath, "rb") as file:
                    data = file.read()
                    hasher = hashlib.sha1()
                    hasher.update(data)
                    self.set_header("Etag", '"%s"' % hasher.hexdigest())
                    if include_body:
                        self.write(data)
                    else:
                        assert self.request.method == "HEAD"
                        self.set_header("Content-Length", len(data))
            
        self.finish()
    
    def set_extra_headers(self, path):
        """For subclass to add extra headers to the response"""
        pass
    
    def get_cache_time(self, path, modified, mime_type):
        """Override to customize cache control behavior.
        
        Return a positive number of seconds to trigger aggressive caching or 0
        to mark resource as cacheable, only.
        
        By default returns cache expiry of 10 years for resources requested
        with "v" argument.
        """
        return self.CACHE_MAX_AGE if "v" in self.request.arguments else 0
    
    @classmethod
    def make_static_url(cls, settings, path):
        """Constructs a versioned url for the given path.
        
        This method may be overridden in subclasses (but note that it is
        a class method rather than an instance method).

        ``settings`` is the `Application.settings` dictionary.  ``path``
        is the static path being requested.  The url returned should be
        relative to the current host.
        """
        static_url_prefix = settings.get('static_url_prefix', '/static/')
        version_hash = cls.get_version(settings, path)
        if version_hash:
            return static_url_prefix + path + "?v=" + version_hash
        return static_url_prefix + path
    
    @classmethod
    def get_version(cls, settings, path):
        """Generate the version string to be used in static URLs.
        
        This method may be overridden in subclasses (but note that it
        is a class method rather than a static method).  The default
        implementation uses a hash of the file's contents.
        
        ``settings`` is the `Application.settings` dictionary and ``path``
        is the relative location of the requested asset on the filesystem.
        The returned value should be a string, or ``None`` if no version
        could be determined.
        """
        abs_path = os.path.join(settings["static_path"], path)
        abs_path = cls.abspath(abs_path)
        with cls._lock:
            hashes = cls._static_hashes
            if abs_path not in hashes:
                try:
                    f = open(abs_path, "rb")
                    hashes[abs_path] = hashlib.md5(f.read()).hexdigest()
                    f.close()
                except Exception:
                    logging.error("Could not open static file %r", path)
                    hashes[abs_path] = None
            hsh = hashes.get(abs_path)
            if hsh:
                return hsh[:5]
        return None
    
    def parse_url_path(self, url_path):
        """Converts a static URL path into a filesystem path.
        
        ``url_path`` is the path component of the URL with
        ``static_url_prefix`` removed.  The return value should be
        filesystem path relative to ``static_path``.
        """
        if os.path.sep != "/":
            url_path = url_path.replace("/", os.path.sep)
        return url_path

def authenticated(method):
    """Decorate methods with this to require that the user be logged in."""
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if not self.current_user:
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
            raise tornado.web.HTTPError(403)
        return method(self, *args, **kwargs)
    return wrapper
    
def is_staff(method):
    """Decorate methods with this to require that the user be logged in."""
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if not self.current_user or not self.current_user.is_staff:
            raise tornado.web.HTTPError(404)
        return method(self, *args, **kwargs)
    return wrapper
    
def is_superuser(method):
    """Decorate methods with this to require that the user be logged in."""
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if not self.current_user or not self.current_user.is_superuser:
            raise tornado.web.HTTPError(404)
        return method(self, *args, **kwargs)
    return wrapper
