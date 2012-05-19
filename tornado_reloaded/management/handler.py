#!/usr/bin/env python
# -*- coding: utf-8 -*-
# encoding: utf-8
"""
handler.py

Created by Olivier Hardy on 2011-10-10.
Copyright (c) 2011 Olivier Hardy. All rights reserved.
"""

import os
import sys
import argparse
from functools import partial

import commands

from loading import get_command
from loading import get_commands

from tornado.options import options
import tornado.options

import tornado_reloaded.applications

class MyAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        print parser, namespace, values, option_string
        # Set optional arguments to True or False
        # if option_string:
        #             attr = True if values else False
        #             setattr(namespace, self.dest, attr)
        #
        #         # Modify value of "input" in the namespace
        #         setattr(namespace, self.dest, values)
        argparse.Action(self, parser, namespace, values, option_string)
        print parser, namespace, values, option_string

class ManagementUtility(object):
    """
    Encapsulates the logic of the django-admin.py and manage.py utilities.
    
    A ManagementUtility has a number of commands, which can be manipulated
    by editing the self.commands dictionary.
    """
    def __init__(self, argv=None):
        self.argv = argv or sys.argv[:]
        self.prog_name = os.path.basename(self.argv[0])
    
    def get_envs(self):
        """docstring for get_envs"""
        path = os.path.join(os.getcwd(), 'envs')
        new_envs = []
        if os.path.exists(path):
            envs = os.listdir(path)
            for e in envs:
                new_envs.append(os.path.splitext(e)[0])
        
        return new_envs
    
    def get_parser(self):
        """docstring for get_root_parser"""
        parser = argparse.ArgumentParser(prog='tornado')
        subparsers = parser.add_subparsers(dest='subparser', help='sub-command help')
        
        for name, command in get_commands().items():
            command   = command()
            
            subparser = subparsers.add_parser(name, help=command.get_help())#, parents=parents) #, aliases=command.get_aliases())
            command._add_arguments(self, subparser)
        
        return parser
    
    def autocomplete(self):
        """
        Output completion suggestions for BASH.
        
        The output of this function is passed to BASH's `COMREPLY` variable and
        treated as completion suggestions. `COMREPLY` expects a space
        separated string as the result.
        
        The `COMP_WORDS` and `COMP_CWORD` BASH environment variables are used
        to get information about the cli input. Please refer to the BASH
        man-page for more information about this variables.
        
        Subcommand options are saved as pairs. A pair consists of
        the long option string (e.g. '--exclude') and a boolean
        value indicating if the option requires arguments. When printing to
        stdout, a equal sign is appended to options which require arguments.
        
        Note: If debugging this function, it is recommended to write the debug
        output in a separate file. Otherwise the debug output will be treated
        and formatted as potential completion suggestions.
        """
        # Don't complete if user hasn't sourced bash_completion file.
        if 'TORNADO_AUTO_COMPLETE' not in os.environ:
            return
        
        cwords = os.environ['COMP_WORDS'].split()[1:]
        cword = int(os.environ['COMP_CWORD'])
        
        try:
            curr = cwords[cword-1]
        except IndexError:
            curr = ''
        
        envs = self.get_envs()
        
        subcommands = get_commands().keys() + envs + ['help']
        options = [('--help', None)]
        
        # subcommand
        if cword == 1:
            print ' '.join(sorted(filter(lambda x: x.startswith(curr), subcommands)))
        # subcommand options
        # special case: the 'help' subcommand has no options
        elif cwords[0] in subcommands and cwords[0] != 'help':
            subcommand_cls = self.fetch_command(cwords[0])
            # special case: 'runfcgi' stores additional options as
            # 'key=value' pairs
            if cwords[0] == 'runfcgi':
                from django.core.servers.fastcgi import FASTCGI_OPTIONS
                options += [(k, 1) for k in FASTCGI_OPTIONS]
            # special case: add the names of installed apps to options
            elif cwords[0] in ('dumpdata', 'reset', 'sql', 'sqlall',
                               'sqlclear', 'sqlcustom', 'sqlindexes',
                               'sqlreset', 'sqlsequencereset', 'test'):
                try:
                    from django.conf import settings
                    # Get the last part of the dotted path as the app name.
                    options += [(a.split('.')[-1], 0) for a in settings.INSTALLED_APPS]
                except ImportError:
                    # Fail silently if DJANGO_SETTINGS_MODULE isn't set. The
                    # user will find out once they execute the command.
                    pass
            options += [(s_opt.get_opt_string(), s_opt.nargs) for s_opt in
                        subcommand_cls.option_list]
            # filter out previously specified options from available options
            prev_opts = [x.split('=')[0] for x in cwords[1:cword-1]]
            options = filter(lambda (x, v): x not in prev_opts, options)
            
            # filter options by current input
            options = sorted([(k, v) for k, v in options if k.startswith(curr)])
            for option in options:
                opt_label = option[0]
                # append '=' to options which require args
                if option[1]:
                    opt_label += '='
                print opt_label
        sys.exit(1)
    
    
    def execute(self):
        """
        Given the command-line arguments, this figures out which subcommand is
        being run, creates a parser appropriate to that command, and runs it.
        """
        
        current_dir = os.getcwd()
        sys.path.append(current_dir)
        
        parser = self.get_parser()
        
        self.autocomplete()
        
        result = parser.parse_args(self.argv[1:])
        
        kwargs   = vars(result)
        
        env = kwargs.pop('env', None)
        if env is not None:
            options['env'].set(unicode(env))
        
        tornado.options.parse_command_line()
        
        if env is not None:
            tornado.options.parse_config_file(os.path.join(current_dir, 'envs/base.py'))
            if '.' in options.env:
                tornado.options.parse_config_file(os.path.join(current_dir, 'envs/%s.py' % (options.env.split('.')[0], )))
            tornado.options.parse_config_file(os.path.join(current_dir, 'envs/%s.py' % (options.env, )))
        
        command = get_command(kwargs.pop('subparser'))()
        
        if command.require_env and env is None:
            raise Exception('This command require env')
        
        command.handle(**kwargs)

def execute(argv=None):
    """docstring for handle"""
    utility = ManagementUtility(argv)
    utility.execute()
