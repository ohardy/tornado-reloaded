# #!/usr/bin/env python
# # -*- coding: utf-8 -*-
# # encoding: utf-8
# """
# base.py
# 
# Created by Olivier Hardy on 2011-11-17.
# Copyright (c) 2011 Olivier Hardy. All rights reserved.
# """
# 
# import json
# import logging
# import functools
# from datetime import datetime
# 
# import tornado
# import tornado.locale
# from tornado.options import options
# from tornado import gen
# 
# from tornado_reloaded.utils import check_auth
# from tornado_reloaded.utils import check_hash
# 
# from tornado_reloaded.auth import User
# from tornado_reloaded.auth import AnonymousUser
# 
# logger = logging.getLogger(__name__)
# 
# def auth_by_cookie(method):
#     @functools.wraps(method)
#     def wrapper(self, *args, **kwargs):
#         if self.current_user is None and self.get_secure_cookie('user'):
#             self.do_auth(self.async_callback(method, self, *args, **kwargs))
#         else:
#             return method(self, *args, **kwargs)
#     return wrapper
# 
# def send_message_to_user(username, message, data):
#     """docstring for send_message"""
#     logger.info(u'send_message_to_user %s : %s | %s' % (username, message, data, ))
#     c.publish(u'users.%s.%s' % (username, message, ), json.dumps(data))
# 
# def get_method(obj, method):
#     """docstring for get_method"""
#     return getattr(obj, method)
# 
# class AsyncCurrentUserMixin:
#     """docstring for AsyncCurrentUserMixin"""
#     
#     def prepare(self, callback):
#         """docstring for prepare"""
#         callback()
#     
#     @gen.engine
#     def _prepare(self, method, *args, **kwargs):
#         """docstring for before_prepare"""
#         _ = yield gen.Task(self._load_current_user)
#         _ = yield gen.Task(self.prepare)
#         
#         if not self._finished:
#             args, kwargs = self._decode_args_and_kwargs(*args, **kwargs)
#             
#             if isinstance(method, basestring):
#                 method = getattr(self.__class__, method)
#             
#             if not method.__self__:
#                 method = functools.partial(method, self)
# 
#             try:
#                 method(*args, **kwargs)
#             except Exception as e:
#                 self._handle_request_exception(e)
#             
#             if self._auto_finish and not self._finished:
#                 self.finish()
#     
#     @gen.engine
#     def _load_current_user(self, callback):
#         """docstring for _load_current_user"""
#         if self.current_user is None and self.application.settings.get('cookie_secret') and self.get_secure_cookie('email'):
#             self._current_user = yield gen.Task(self.load_current_user)
#         else:
#             self._current_user = AnonymousUser()
#         
#         callback()
#     
#     @gen.engine
#     def load_current_user(self, callback):
#         """docstring for get_current_user"""
#         email           = self.get_secure_cookie('email')
#         password_hash   = self.get_secure_cookie('p_hash')
#         
#         #Use user_properties for fields arg
#         response = yield gen.Task(self.db.users.find_one, {
#                     'email' : email
#                 })
#         
#         if response:
#             if check_hash(password_hash, response):
#                 def mod_callback3(insert_response):
#                     """docstring for mod_callback"""
#                     kwargs = {}
#                     for name in options.user_properties:
#                         kwargs[name] = response.get(name)
#                     callback(User(
#                         email             = response['email'],
#                         username          = response['username'],
#                         id                = response['_id'],
#                         is_superuser      = response.get('is_superuser', False),
#                         is_staff          = response.get('is_staff', False),
#                         **kwargs
#                     ))              
#                 self.db.users.update({
#                         "_id": response['_id']
#                     }, {
#                         '$set' : {
#                             'lastActivity': datetime.utcnow()
#                         }
#                     },
#                     callback=mod_callback3
#                 )
#                 return
# 
#         self.clear_all_cookies()
#         callback(AnonymousUser())
# 
# # class FullAsyncRequestHandler(AsyncCurrentUserMixin):
# #     pass
# # 
# # class BaseHandler(object):
# #     @property
# #     def db(self):
# #         return self.application.db
# #     
# #     def write_error(self, status_code, **kwargs):
# #         """Override to implement custom error pages.
# #         
# #         ``write_error`` may call `write`, `render`, `set_header`, etc
# #         to produce output as usual.
# #         
# #         If this error was caused by an uncaught exception, an ``exc_info``
# #         triple will be available as ``kwargs["exc_info"]``.  Note that this
# #         exception may not be the "current" exception for purposes of
# #         methods like ``sys.exc_info()`` or ``traceback.format_exc``.
# #         
# #         For historical reasons, if a method ``get_error_html`` exists,
# #         it will be used instead of the default ``write_error`` implementation.
# #         ``get_error_html`` returned a string instead of producing output
# #         normally, and had different semantics for exception handling.
# #         Users of ``get_error_html`` are encouraged to convert their code
# #         to override ``write_error`` instead.
# #         """
# #         if status_code in (404, 400, ):
# #             self.render('%d.html' % (status_code, ))
# #         else:
# #             super(BaseHandler, self).write_error(status_code, **kwargs)
# # 
# # class LocaleMixin(object):
# #     def get_user_locale(self):
# #         print 'get_user_locale'
# #         return tornado.locale.Locale.get_closest('fr_FR')