#!/usr/bin/env python
# -*- coding: utf-8 -*-
# encoding: utf-8
"""
server.py

Created by Olivier Hardy on 2012-01-09.
Copyright (c) 2011 Olivier Hardy. All rights reserved.
"""

import os
import re
import glob
import sys
import fnmatch
from itertools import dropwhile
from subprocess import PIPE, Popen

from tornado_reloaded.management import Command

from tornado_reloaded.servers import runserver

plural_forms_re = re.compile(r'^(?P<value>"Plural-Forms.+?\\n")\s*$', re.MULTILINE | re.DOTALL)

def copy_plural_forms(msgs, locale, domain, verbosity):
    """
    Copies plural forms header contents from a Django catalog of locale to
    the msgs string, inserting it at the right place. msgs should be the
    contents of a newly created .po file.
    """
    import tornado
    tornado_dir = os.path.normpath(os.path.join(os.path.dirname(tornado.__file__)))
    # if domain == 'djangojs':
    #     domains = ('djangojs', 'django')
    # else:
    
    domains = ('tornado',)
    for domain in domains:
        tornado_po = os.path.join(tornado_dir, 'reloaded', 'locale', locale, 'LC_MESSAGES', '%s.po' % domain)
        if os.path.exists(tornado_po):
            m = plural_forms_re.search(open(tornado_po, 'rU').read())
            if m:
                if verbosity > 1:
                    sys.stderr.write("copying plural forms: %s\n" % m.group('value'))
                lines = []
                seen = False
                for line in msgs.split('\n'):
                    if not line and not seen:
                        line = '%s\n' % m.group('value')
                        seen = True
                    lines.append(line)
                msgs = '\n'.join(lines)
                break
    
    # lines = []
    # msgs = '\n'.join(lines)
    return msgs

def templatize(src, origin=None):
    """
    Turns a Django template into something that is understood by xgettext. It
    does so by translating the Django translation tags into standard gettext
    function invocations.
    """
    from django.template import (Lexer, TOKEN_TEXT, TOKEN_VAR, TOKEN_BLOCK,
            TOKEN_COMMENT, TRANSLATOR_COMMENT_MARK)
    out = StringIO()
    message_context = None
    intrans = False
    inplural = False
    singular = []
    plural = []
    incomment = False
    comment = []
    
    from django.utils.translation import strip_blocktrans
    
    for t in Lexer(src, origin).tokenize():
        if incomment:
            if t.token_type == TOKEN_BLOCK and t.contents == 'endcomment':
                content = ''.join(comment)
                translators_comment_start = None
                for lineno, line in enumerate(content.splitlines(True)):
                    if line.lstrip().startswith(TRANSLATOR_COMMENT_MARK):
                        translators_comment_start = lineno
                for lineno, line in enumerate(content.splitlines(True)):
                    if translators_comment_start is not None and lineno >= translators_comment_start:
                        out.write(' # %s' % line)
                    else:
                        out.write(' #\n')
                incomment = False
                comment = []
            else:
                comment.append(t.contents)
        elif intrans:
            if t.token_type == TOKEN_BLOCK:
                endbmatch = endblock_re.match(t.contents)
                pluralmatch = plural_re.match(t.contents)
                if endbmatch:
                    singular = strip_blocktrans(''.join(singular))
                    if inplural:
                        if message_context:
                            out.write(' npgettext(%r, %r, %r,count) ' % (message_context, ''.join(singular), ''.join(plural)))
                        else:
                            out.write(' ngettext(%r, %r, count) ' % (''.join(singular), ''.join(plural)))
                        for part in singular:
                            out.write(blankout(part, 'S'))
                        for part in plural:
                            out.write(blankout(part, 'P'))
                    else:
                        if message_context:
                            out.write(' pgettext(%r, %r) ' % (message_context, ''.join(singular)))
                        else:
                            out.write(' gettext(%r) ' % ''.join(singular))
                        for part in singular:
                            out.write(blankout(part, 'S'))
                    message_context = None
                    intrans = False
                    inplural = False
                    singular = []
                    plural = []
                elif pluralmatch:
                    inplural = True
                else:
                    filemsg = ''
                    if origin:
                        filemsg = 'file %s, ' % origin
                    raise SyntaxError("Translation blocks must not include other block tags: %s (%sline %d)" % (t.contents, filemsg, t.lineno))
            elif t.token_type == TOKEN_VAR:
                if inplural:
                    plural.append('%%(%s)s' % t.contents)
                else:
                    singular.append('%%(%s)s' % t.contents)
            elif t.token_type == TOKEN_TEXT:
                contents = t.contents.replace('%', '%%')
                if inplural:
                    plural.append(contents)
                else:
                    singular.append(contents)
        else:
            if t.token_type == TOKEN_BLOCK:
                imatch = inline_re.match(t.contents)
                bmatch = block_re.match(t.contents)
                cmatches = constant_re.findall(t.contents)
                if imatch:
                    g = imatch.group(1)
                    if g[0] == '"':
                        g = g.strip('"')
                    elif g[0] == "'":
                        g = g.strip("'")
                    if imatch.group(2):
                        # A context is provided
                        context_match = context_re.match(imatch.group(2))
                        message_context = context_match.group(1)
                        if message_context[0] == '"':
                            message_context = message_context.strip('"')
                        elif message_context[0] == "'":
                            message_context = message_context.strip("'")
                        out.write(' pgettext(%r, %r) ' % (message_context, g))
                        message_context = None
                    else:
                        out.write(' gettext(%r) ' % g)
                elif bmatch:
                    for fmatch in constant_re.findall(t.contents):
                        out.write(' _(%s) ' % fmatch)
                    if bmatch.group(1):
                        # A context is provided
                        context_match = context_re.match(bmatch.group(1))
                        message_context = context_match.group(1)
                        if message_context[0] == '"':
                            message_context = message_context.strip('"')
                        elif message_context[0] == "'":
                            message_context = message_context.strip("'")
                    intrans = True
                    inplural = False
                    singular = []
                    plural = []
                elif cmatches:
                    for cmatch in cmatches:
                        out.write(' _(%s) ' % cmatch)
                elif t.contents == 'comment':
                    incomment = True
                else:
                    out.write(blankout(t.contents, 'B'))
            elif t.token_type == TOKEN_VAR:
                parts = t.contents.split('|')
                cmatch = constant_re.match(parts[0])
                if cmatch:
                    out.write(' _(%s) ' % cmatch.group(1))
                for p in parts[1:]:
                    if p.find(':_(') >= 0:
                        out.write(' %s ' % p.split(':',1)[1])
                    else:
                        out.write(blankout(p, 'F'))
            elif t.token_type == TOKEN_COMMENT:
                out.write(' # %s' % t.contents)
            else:
                out.write(blankout(t.contents, 'X'))
    return out.getvalue()

def find_files(root, ignore_patterns, verbosity, symlinks=False):
    """
    Helper function to get all files in the given root.
    """
    all_files = []
    for (dirpath, dirnames, filenames) in walk(".", followlinks=symlinks):
        for f in filenames:
            norm_filepath = os.path.normpath(os.path.join(dirpath, f))
            if is_ignored(norm_filepath, ignore_patterns):
                if verbosity > 1:
                    sys.stdout.write('ignoring file %s in %s\n' % (f, dirpath))
            else:
                all_files.extend([(dirpath, f)])
    all_files.sort()
    return all_files

def is_ignored(path, ignore_patterns):
    """
    Helper function to check if the given path should be ignored or not.
    """
    
    for pattern in ignore_patterns:
        if fnmatch.fnmatchcase(path, pattern):
            return True
    
    print path, ignore_patterns
    return False

def walk(root, topdown=True, onerror=None, followlinks=False):
    """
    A version of os.walk that can follow symlinks for Python < 2.6
    """
    for dirpath, dirnames, filenames in os.walk(root, topdown, onerror):
        yield (dirpath, dirnames, filenames)
        if followlinks:
            for d in dirnames:
                p = os.path.join(dirpath, d)
                if os.path.islink(p):
                    for link_dirpath, link_dirnames, link_filenames in walk(p):
                        yield (link_dirpath, link_dirnames, link_filenames)

def _popen(cmd):
    """
    Friendly wrapper around Popen for Windows
    """
    p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE, close_fds=os.name != 'nt', universal_newlines=True)
    return p.communicate()

class MakemessagesCommand(Command):
    """docstring for ServerCommand"""
    name        = 'makemessages'
    require_env = False
    
    def handle(self):
        """docstring for handle"""
        locale = None
        
        ignore_patterns = ['.git/*', '.svn/*', 'tornado.egg-info/*', 'tornado/test/*', 'build/*', 'demos/*']
        
        if os.path.isdir(os.path.join('tornado', 'reloaded', 'locale')):
            localedir = os.path.abspath(os.path.join('tornado', 'reloaded', 'locale'))
            invoked_for_django = True
            # Ignoring all contrib apps
            ignore_patterns += ['website/*']
        elif os.path.isdir('locale'):
            localedir = os.path.abspath('locale')
        else:
            raise Exception('locale folder is required')
        
        # We require gettext version 0.15 or newer.
        output = _popen('xgettext --version')[0]
        match = re.search(r'(?P<major>\d+)\.(?P<minor>\d+)', output)
        if match:
            xversion = (int(match.group('major')), int(match.group('minor')))
            if xversion < (0, 15):
                raise Exception("Tornado internationalization requires GNU gettext 0.15 or newer. You are using version %s, please upgrade your gettext toolset." % match.group())
        
        languages = []
        if locale is not None:
            languages.append(locale)
        elif all:
            locale_dirs = filter(os.path.isdir, glob.glob('%s/*' % localedir))
            languages = [os.path.basename(l) for l in locale_dirs]
        
        domain             = 'tornado'
        extensions         = ['.html', '.txt']
        verbosity          = 1
        wrap               = ''
        symlinks           = False
        invoked_for_django = False
        no_obsolete        = False
        
        for locale in languages:
            if verbosity > 0:
                print "processing language", locale
            basedir = os.path.join(localedir, locale, 'LC_MESSAGES')
            if not os.path.isdir(basedir):
                os.makedirs(basedir)
            
            pofile = os.path.join(basedir, '%s.po' % domain)
            potfile = os.path.join(basedir, '%s.pot' % domain)
            
            if os.path.exists(potfile):
                os.unlink(potfile)
            
            for dirpath, file in find_files(".", ignore_patterns, verbosity, symlinks=symlinks):
                file_base, file_ext = os.path.splitext(file)
                
                if dirpath.startswith('./static/'):
                    continue
                # print file_base, file_ext
                # if domain == 'djangojs' and file_ext in extensions:
                #                     if verbosity > 1:
                #                         sys.stdout.write('processing file %s in %s\n' % (file, dirpath))
                #                     src = open(os.path.join(dirpath, file), "rU").read()
                #                     src = prepare_js_for_gettext(src)
                #                     thefile = '%s.c' % file
                #                     f = open(os.path.join(dirpath, thefile), "w")
                #                     try:
                #                         f.write(src)
                #                     finally:
                #                         f.close()
                #                     cmd = (
                #                         'xgettext -d %s -L C %s --keyword=gettext_noop '
                #                         '--keyword=gettext_lazy --keyword=ngettext_lazy:1,2 '
                #                         '--keyword=pgettext:1c,2 --keyword=npgettext:1c,2,3 '
                #                         '--from-code UTF-8 --add-comments=Translators -o - "%s"' % (
                #                             domain, wrap, os.path.join(dirpath, thefile)
                #                         )
                #                     )
                #                     msgs, errors = _popen(cmd)
                #                     if errors:
                #                         os.unlink(os.path.join(dirpath, thefile))
                #                         if os.path.exists(potfile):
                #                             os.unlink(potfile)
                #                         raise CommandError(
                #                             "errors happened while running xgettext on %s\n%s" %
                #                             (file, errors))
                #                     if msgs:
                #                         old = '#: ' + os.path.join(dirpath, thefile)[2:]
                #                         new = '#: ' + os.path.join(dirpath, file)[2:]
                #                         msgs = msgs.replace(old, new)
                #                         if os.path.exists(potfile):
                #                             # Strip the header
                #                             msgs = '\n'.join(dropwhile(len, msgs.split('\n')))
                #                         else:
                #                             msgs = msgs.replace('charset=CHARSET', 'charset=UTF-8')
                #                         f = open(potfile, 'ab')
                #                         try:
                #                             f.write(msgs)
                #                         finally:
                #                             f.close()
                #                     os.unlink(os.path.join(dirpath, thefile))
                if domain == 'tornado' and (file_ext == '.py' or file_ext in extensions):
                    thefile = file
                    orig_file = os.path.join(dirpath, file)
                    if file_ext in extensions:
                        src = open(orig_file, "rU").read()
                        #
                        from tornado import template
                        
                        kwargs = {}
                        tpl = template.Loader(os.path.abspath('templates'), **kwargs)
                        
                        # tpl = template.Loader()
                        try:
                            hop_orig_file = orig_file.replace('./templates/', './')
                            f = tpl.load(hop_orig_file)
                        
                        except Exception as e:
                            pass
                        else:
                            thefile = '%s.py' % file
                            # print os.path.join(dirpath, thefile)
                            f2 = open(os.path.join(dirpath, thefile), "w")
                            try:
                                f2.write(f.code)
                            finally:
                                f2.close()
                    if verbosity > 1:
                        sys.stdout.write('processing file %s in %s\n' % (file, dirpath))
                    cmd = (
                        'xgettext -d %s -L Python %s --keyword=gettext_noop --from-code UTF-8 '
                        '--add-comments=Translators -o - "%s"' % (
                            domain, wrap, os.path.join(dirpath, thefile))
                    )
                    
                    msgs, errors = _popen(cmd)
                    if errors:
                        if thefile != file:
                            os.unlink(os.path.join(dirpath, thefile))
                        if os.path.exists(potfile):
                            os.unlink(potfile)
                        raise Exception(
                            "errors happened while running xgettext on %s\n%s" %
                            (file, errors))
                    if msgs:
                        if thefile != file:
                            old = '#: ' + os.path.join(dirpath, thefile)[2:]
                            new = '#: ' + orig_file[2:]
                            msgs = msgs.replace(old, new)
                        if os.path.exists(potfile):
                            # Strip the header
                            msgs = '\n'.join(dropwhile(len, msgs.split('\n')))
                        else:
                            msgs = msgs.replace('charset=CHARSET', 'charset=UTF-8')
                        
                        f = open(potfile, 'ab')
                        try:
                            f.write(msgs)
                        finally:
                            f.close()
                    if thefile != file:
                        os.unlink(os.path.join(dirpath, thefile))
            
            if os.path.exists(potfile):
                msgs, errors = _popen('msguniq %s --to-code=utf-8 "%s"' %
                                      (wrap, potfile))
                if errors:
                    os.unlink(potfile)
                    raise Exception(
                        "errors happened while running msguniq\n%s" % errors)
                if os.path.exists(pofile):
                    f = open(potfile, 'w')
                    try:
                        f.write(msgs)
                    finally:
                        f.close()
                    msgs, errors = _popen('msgmerge %s -q "%s" "%s"' %
                                          (wrap, pofile, potfile))
                    if errors:
                        os.unlink(potfile)
                        raise CommandError(
                            "errors happened while running msgmerge\n%s" % errors)
                elif not invoked_for_django:
                    msgs = copy_plural_forms(msgs, locale, domain, verbosity)
                msgs = msgs.replace(
                    "#. #-#-#-#-#  %s.pot (PACKAGE VERSION)  #-#-#-#-#\n" % domain, "")
                
                print 'POfile', pofile
                f = open(pofile, 'wb')
                try:
                    f.write(msgs)
                finally:
                    f.close()
                os.unlink(potfile)
                if no_obsolete:
                    msgs, errors = _popen('msgattrib %s -o "%s" --no-obsolete "%s"' %
                                          (wrap, pofile, pofile))
                    if errors:
                        raise Exception(
                            "errors happened while running msgattrib\n%s" % errors)
            
