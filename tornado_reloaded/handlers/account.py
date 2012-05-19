#!/usr/bin/env python
# -*- coding: utf-8 -*-
# encoding: utf-8
"""
account.py

Created by Olivier Hardy on 2011-11-21.
Copyright (c) 2011 Olivier Hardy. All rights reserved.
"""

from datetime import datetime
import hashlib

import tornado.web
from tornado import gen

from tornado.options import options

# from base import AsyncCurrentUserMixin, BaseHandler

from tornado_reloaded.web import RequestHandler
from tornado_reloaded.utils import check_auth
from tornado_reloaded.utils import get_random_string
from tornado_reloaded.validations import is_valid_email

method   = 'sha512'

class LoginHandler(RequestHandler):
    def get(self):
        self.render('account/login.html')
    
    @tornado.web.asynchronous
    def post(self):
        username        = self.get_argument('username', '')
        email           = self.get_argument('email', '')
        password        = self.get_argument('password', '')
        
        if username == '' or password == '':
            self.render('account/login.html')
            return
            
        self.db.users.find(
            specs = {
            '$or' : [{
                    'username' : username
                }, {
                    'email' : email
                }]
        
        }, callback=self.async_callback(self._on_find)).loop()
    
    @tornado.web.asynchronous
    def _on_find(self, response):
        for response_user in response:
            username = response_user.get('username')
            email    = response_user.get('email')
            if username is None and email is None:
                raise Exception('Username or email is required')
            
            password = self.get_argument('password')
            
            # print '_on_find', check_auth(response_user, password, email=email, username=username)
            if check_auth(response_user, password, email=email, username=username):
                # print 'OK'
                if email is not None:
                    self.set_secure_cookie("email",     email)
                if username is not None:
                    self.set_secure_cookie("user",      username)
                self.set_secure_cookie("p_hash",    response_user['password']['hash'])
                # self.redirect(self.reverse_url('homepage:index'))
                # return
                
                self.db.users.update({
                        "_id": response_user['_id']
                    }, {
                        '$set' : {
                            'lastLogin': datetime.utcnow()
                        }
                    },
                    callback=self._on_update
                )
                return
        
        self.redirect(self.reverse_url('account:login'))
    
    def _on_update(self, response):
        self.redirect(self.reverse_url('homepage:index'))

class LogoutHandler(RequestHandler):
    def get(self):
        self.render('account/logout.html')
    
    def post(self):
        """docstring for post"""
        self.clear_all_cookies()
        self.redirect(self.reverse_url('homepage'))

class RegisterHandler(RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        self.render('account/register.html')
    
    @tornado.web.asynchronous
    def post(self):
        username        = self.get_argument('username')
        email           = self.get_argument('email')
        password        = self.get_argument('password')
        repeat_password = self.get_argument('repeat-password')
        
        if password != repeat_password:
            raise Exception('Password doesnt match')
        
        self.db.users.find_one({
            '$or': [{
                'username' : username
                },{
                'email': email
                }]
        }, callback=self._on_find)
    
    @tornado.web.asynchronous
    def _on_find(self, response):
        if not response:
            username = self.get_argument('username')
            email    = self.get_argument('email')
            password = self.get_argument('password')
            
            p        = getattr(hashlib, method)()
            salt     = get_random_string()
            p.update("%s%s" % (salt, password, ))
            password = p.hexdigest()
            
            self.db.users.insert({
                'username' : username,
                'email' : email,
                'password' : {
                    'hash'      : password,
                    'method'    : method,
                    'salt'      : salt
                },
                'creationDate' : datetime.utcnow()
            }, callback=self._on_save)
        else:
            raise Exception('Username already exist')
    
    def _on_save(self, response):
        if not response:
            raise tornado.web.HTTPError(500)
        self.render('account/register-ok.html', user=response)

class UserHandler(RequestHandler):
    @tornado.web.asynchronous
    def get(self, username=None):
        username = username or self.current_user.username
        self.db.users.find_one({
            'username': username
        }, callback=self._on_response)
    
    def _on_response(self, response):
        if not response:
            raise tornado.web.HTTPError(500)
        self.render('account/detail.html', user=response)

class AccountEditHandler(RequestHandler):
    @tornado.web.asynchronous
    @gen.engine
    def get(self, username=None):
        username = username or self.current_user.username
        response = yield gen.Task(self.db.users.find_one, {
            'username': username
        })
        
        if not response:
            raise tornado.web.HTTPError(500)
        
        self.render('account/detail.html', user=response)

class InviteHandler(RequestHandler):
    @tornado.web.asynchronous
    
    def prepare(self, callback):
        """docstring for initialize"""
        if not options.invitation_enabled or not self.current_user.can_invite:
            raise tornado.web.HTTPError(404)
        
        callback()
    
    def get(self):
        self.db.users_invitations.find_one({
                'user' : self.current_user.username
            }, callback=self._on_find_invitations)
    
    @tornado.web.asynchronous
    def _on_find_invitations(self, response):
        self.render('account/invite.html', user_invitation=response, email='', errors={})
    
    @tornado.web.asynchronous
    def post(self):
        errors = {}
        _ = self.locale.translate
        try:
            email = self.get_argument('email')
            if not is_valid_email(email):
                errors['email'] = _('A valid email is required')
        except:
            errors['email'] = _('A valid email is required')
        else:
            if email == self.current_user.email:
                errors['email'] = _('You cant invite yourself')
        
        if errors:
            self.render('account/invite.html', email=self.get_argument('email', ''), errors = errors)
        else:
            self.db.users_invitations.find_one({
                'user' : self.current_user.username,
                'invitations.email' : email
            }, callback=self._on_find_invitation)
    
    @tornado.web.asynchronous
    def _on_find_invitation(self, response):
        _ = self.locale.translate
        if not response:
            email = self.get_argument('email')
            self.db.users_invitations.update({
                    'user' : self.current_user.username
                }, {
                    '$set' : {
                        'user' : self.current_user.username
                    },
                    '$push' : {
                        'invitations' : {
                            'email' : email,
                            'creation_date' : datetime.utcnow()
                        }
                    }
                },
                upsert   = True,
                callback = self._on_save)
        else:
            self.render('account/invite.html', email=self.get_argument('email', ''), errors = {
                'email' : _('You already send an invitation to this person')
            })
    
    def _on_save(self, response):
        self.render('account/invite-ok.html', invite=response)
