#!/usr/bin/env python
# -*- coding: utf-8 -*-
# encoding: utf-8
"""
server.py

Created by Olivier Hardy on 2012-01-09.
Copyright (c) 2011 Olivier Hardy. All rights reserved.
"""

import os
import sys
import codecs

from tornado_reloaded.management import Command

from tornado_reloaded.servers import runserver

def has_bom(fn):
    f = open(fn, 'r')
    sample = f.read(4)
    return sample[:3] == '\xef\xbb\xbf' or \
            sample.startswith(codecs.BOM_UTF16_LE) or \
            sample.startswith(codecs.BOM_UTF16_BE)

class CompilemessagesCommand(Command):
    """docstring for ServerCommand"""
    name        = 'compilemessages'
    require_env = False
    
    def handle(self):
        """docstring for handle"""
        basedirs = ['locale']
        locale   = ''
        wrap     = ''
        
        import tornado
        tornado_dir = os.path.normpath(os.path.join(os.path.dirname(tornado.__file__)))
        base_fn2 = os.path.join(tornado_dir, 'reloaded', 'locale')
        
        for basedir in basedirs:
            locale = None
            # if locale:
                # basedir = os.path.join(basedir, locale, 'LC_MESSAGES')
            for dirpath, dirnames, filenames in os.walk(basedir):
                if dirnames and dirnames[0] == 'LC_MESSAGES':
                    locale = dirpath.split('/')[-1]
                
                for f in filenames:
                    if f.endswith('.po'):
                        print 'processing file %s in %s\n' % (f, dirpath)
                        fn = os.path.join(dirpath, f)
                        if has_bom(fn):
                            raise Exception("The %s file has a BOM (Byte Order Mark). Tornado only supports .po files encoded in UTF-8 and without any BOM." % fn)
                        pf = os.path.splitext(fn)[0]
                        # Store the names of the .mo and .po files in an environment
                        # variable, rather than doing a string replacement into the
                        # command, so that we can take advantage of shell quoting, to
                        # quote any malicious characters/escaping.
                        # See http://cyberelk.net/tim/articles/cmdline/ar01s02.html
                        os.environ['tornadocompilemo'] = pf + '.mo'
                        os.environ['tornadocompilepo'] = pf + '.po'
                        os.environ['tornadocompilepo3'] = pf + '2.po'
                        os.environ['tornadocompilepo4'] = pf + '4.po'
                        
                        fn2 = os.path.join(base_fn2, locale, 'LC_MESSAGES', 'tornado.po')
                        
                        if os.path.exists(fn2):
                            if has_bom(fn2):
                                raise Exception("The %s file has a BOM (Byte Order Mark). Tornado only supports .po files encoded in UTF-8 and without any BOM." % fn)
                            
                            pf2 = os.path.splitext(fn2)[0]
                            # print pf2
                            os.environ['tornadocompilepo2'] = pf2 + '.po'
                            
                            if sys.platform == 'win32': # Different shell-variable syntax
                                cmd = 'msgcat -o "%ttornadocompilepo3%" "%tornadocompilepo2%" "%tornadocompilepo%"'
                            else:
                                cmd = 'msgcat -o "$tornadocompilepo3" "$tornadocompilepo2" "$tornadocompilepo"'
                        
                        else:
                            if sys.platform == 'win32': # Different shell-variable syntax
                                cmd = 'msgcat -o "%ttornadocompilepo3%" "%tornadocompilepo%"'
                            else:
                                cmd = 'msgcat -o "$tornadocompilepo3" "$tornadocompilepo"'
                        
                        os.system(cmd)
                        
                        cmd = 'msguniq -o "%s" --to-code=utf-8 "%s"' %(os.environ['tornadocompilepo4'], os.environ['tornadocompilepo3'], )
                        
                        # print cmd
                        
                        os.system(cmd)
                        
                        
                        if sys.platform == 'win32': # Different shell-variable syntax
                            cmd = 'msgfmt --check-format -o "%tornadocompilemo%" "%ttornadocompilepo4%"'
                        else:
                            cmd = 'msgfmt --check-format -o "$tornadocompilemo" "$tornadocompilepo4"'
                        
                        # print cmd
                        
                        os.system(cmd)
                        
                        if os.path.exists(os.environ['tornadocompilepo4']):
                            os.unlink(os.environ['tornadocompilepo4'])
                        if os.path.exists(os.environ['tornadocompilepo3']):
                            os.unlink(os.environ['tornadocompilepo3'])
