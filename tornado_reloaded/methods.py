#!/usr/bin/env python
# -*- coding: utf-8 -*-
# encoding: utf-8
"""
methods.py

Created by Olivier Hardy on 2011-11-22.
Copyright (c) 2011 Olivier Hardy. All rights reserved.
"""

import re
import uuid
import string
from datetime import date
from datetime import datetime

import tornado.escape
import unicodedata

from tornado.options import options
from tornado.web import async
from tornado.web import with_handler

ALPHABET = string.ascii_uppercase + string.ascii_lowercase + string.digits + '-_'
ALPHABET_REVERSE = dict((c, i) for (i, c) in enumerate(ALPHABET))
BASE = len(ALPHABET)
SIGN_CHARACTER = '$'

def html_input(name, value="", input_type="text", label=None, with_p=True):
    """docstring for html_input"""
    string = '<input type="%(input_type)s" name="%(name)s" id="id_%(name)s" value="%(value)s" />'
    string = string % {
        'name' : name,
        'value' : value,
        'input_type' : input_type
    }
    
    if label:
        label_string = '<label for="id_%(name)s">%(label)s</label>' % {
            'name' : name,
            'label' : label
        }
    else:
        label_string = ''
        
    if with_p:
        return '<p>%s%s</p>' % (label_string, string, )
    
    return '%s%s' % (label_string, string, )

def absolute_url(url, https=False):
    """docstring for absolute_url"""
    return u"%s%s%s" % (https and 'https://' or 'http://', options.absolute_base_url, url)

def invitation_enabled():
	"""docstring for invitation_enabled"""
	return options.invitation_enabled

@with_handler
def get_active_class(handler, with_var):
    """docstring for get_active_class"""
    active_menu_item = getattr(handler, 'active_menu_item', '')
    
    if active_menu_item and active_menu_item.startswith(with_var):
        return ' class="active"'
    
    return ''

@with_handler
def get_only_active_class(handler, with_var):
    """docstring for get_active_class"""
    active_menu_item = getattr(handler, 'active_menu_item', '')
    
    if active_menu_item and active_menu_item.startswith(with_var):
        return 'active'
    
    return ''

def int_to_short_id(number):
    if number < 0:
        return SIGN_CHARACTER + int_to_short_id(-number)
    s = []
    while True:
        number, r = divmod(number, BASE)
        s.append(ALPHABET[r])
        if number == 0: break
    return ''.join(reversed(s))


def short_id_to_int(s):
    if s[0] == SIGN_CHARACTER:
        return -short_id_to_int(s[1:])
    n = 0
    for c in s:
        n = n * BASE + ALPHABET_REVERSE[c]
    return n

def short_id_to_uuid(s):
    return uuid.UUID(int=short_id_to_int(s))

def get_short_id():
    return int_to_short_id(uuid.uuid4().int)

def unslugify(value):
    """docstring for unslugify"""
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    return value.replace('-', ' ')

def slugify(value):
    """
    From Django
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.
    """
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = unicode(re.sub('[^\w\s-]', '', value).strip().lower())
    return re.sub('[-\s]+', '-', value)

def remove_whitespaces(value):
    return value.replace(" ", "")

def protect_email(value):
    """docstring for protect_email"""
    return value.replace("@", "(at)")

def url_escape(value):
    """docstring for url_escape"""
    return tornado.escape.url_escape(value)

def escape(value):
    if not isinstance(value, basestring):
        value = unicode(value)
    return tornado.escape.xhtml_escape(value)

@async
@with_handler
def toto(handler, callback):
    handler.db.users.find(spec={})(callback)

def linebreaks_to_html(value):
    """docstring for linebreaks_to_html"""
    return value.replace("\n","<br />\n")

def format_phone(number):
    """docstring for format_phone"""
    number = str(remove_whitespaces(number))
    new_phone = ""
    if number.startswith("+"):
        next = 4
        new_phone = number[0:next] + " "
        number = number[next:]
    
    i = 0
    while i < len(number):
        new_phone += number[i:i+2] + " "
        
        i += 2
    return new_phone

def remove_tags(value, tags):
    """docstring for fname"""
    if isinstance(tags, basestring):
        tags = [re.escape(tag) for tag in tags.split()]
    else:
        tags = [re.escape(tag) for tag in tags]
    
    tags_re = u'(%s)' % u'|'.join(tags)
    starttag_re = re.compile(ur'<%s(/?>|(\s+[^>]*>))' % tags_re, re.U)
    endtag_re = re.compile(u'</%s>' % tags_re)
    value = starttag_re.sub(u'', value)
    value = endtag_re.sub(u'', value)
    return value

#TODO : Add parameters : allowed_attributes and allowed_elements
def sanitize_html(html, acceptable_elements=[], acceptable_attributes=[]):
    """Sanitizes an HTML fragment."""
    
    if isinstance(acceptable_elements, basestring):
        acceptable_elements = [re.escape(tag) for tag in acceptable_elements.split()]
    else:
        acceptable_elements = [re.escape(tag) for tag in acceptable_elements]
    
    if isinstance(acceptable_attributes, basestring):
        acceptable_attributes = [re.escape(tag) for tag in acceptable_attributes.split()]
    else:
        acceptable_attributes = [re.escape(tag) for tag in acceptable_attributes]
    
    import html5lib
    from html5lib import sanitizer, serializer, tokenizer, treebuilders, treewalkers
    from xml.sax.saxutils import escape, unescape
    
    
    from html5lib.constants import tokenTypes
    
    class HTMLSanitizer(tokenizer.HTMLTokenizer, sanitizer.HTMLSanitizerMixin):
        def __init__(self, stream, encoding=None, parseMeta=True, useChardet=True,
                     lowercaseElementName=True, lowercaseAttrName=True):
            
            self.acceptable_elements = acceptable_elements or ('a', 'dl', 'dt', 'em', 'i', 'ins', 'del',
                                     'li', 'ol', 'strong', 'u', 'ul')
            
            self.acceptable_attributes = acceptable_attributes or ('alt', 'href', 'hreflang', 'lang', 'title')
            
            self.allowed_elements = acceptable_elements
            self.allowed_attributes = acceptable_attributes
            self.allowed_css_properties = ()
            self.allowed_css_keywords = ()
            self.allowed_svg_properties = ()
            
            
            tokenizer.HTMLTokenizer.__init__(self, stream, encoding, parseMeta,
                                             useChardet, lowercaseElementName,
                                             lowercaseAttrName)
        
        
        
        def sanitize_token(self, token):
            # accommodate filters which use token_type differently
            token_type = token["type"]
            if token_type in tokenTypes.keys():
                token_type = tokenTypes[token_type]
            
            if token_type in (tokenTypes["StartTag"], tokenTypes["EndTag"], tokenTypes["EmptyTag"]):
                if token["name"] in self.allowed_elements:
                    if token.has_key("data"):
                        attrs = dict([(name,val) for name,val in token["data"][::-1] if name in self.allowed_attributes])
                        for attr in self.attr_val_is_uri:
                            if not attrs.has_key(attr):
                                continue
                            val_unescaped = re.sub("[`\000-\040\177-\240\s]+", '', unescape(attrs[attr])).lower()
                            #remove replacement characters from unescaped characters
                            val_unescaped = val_unescaped.replace(u"\ufffd", "")
                            if (re.match("^[a-z0-9][-+.a-z0-9]*:",val_unescaped) and (val_unescaped.split(':')[0] not in self.allowed_protocols)):
                                del attrs[attr]
                            for attr in self.svg_attr_val_allows_ref:
                                if attr in attrs:
                                    attrs[attr] = re.sub(r'url\s*\(\s*[^#\s][^)]+?\)', ' ', unescape(attrs[attr]))
                        if (token["name"] in self.svg_allow_local_href and 'xlink:href' in attrs and re.search('^\s*[^#\s].*', attrs['xlink:href'])):
                            del attrs['xlink:href']
                        if attrs.has_key('style'):
                            attrs['style'] = self.sanitize_css(attrs['style'])
                        token["data"] = [[name,val] for name,val in attrs.items()]
                    return token
                else:
                    token["data"] = ""
                    
                    if token["type"] in tokenTypes.keys():
                        token["type"] = "Characters"
                    else:
                        token["type"] = tokenTypes["Characters"]
                    del token["name"]
                    return token
            elif token_type == tokenTypes["Comment"]:
                pass
            else:
                return token
        
        def __iter__(self):
            for token in tokenizer.HTMLTokenizer.__iter__(self):
                new_token = self.sanitize_token(token)
                if token is not None:
                    yield token
    
    p = html5lib.HTMLParser(tokenizer=HTMLSanitizer,
                            tree=treebuilders.getTreeBuilder("dom"))
    dom_tree = p.parseFragment(html)
    walker = treewalkers.getTreeWalker("dom")
    stream = walker(dom_tree)
    s = serializer.HTMLSerializer(omit_optional_tags=False,
                                  quote_attr_values=True)
    output_generator = s.serialize(stream)
    return u''.join(output_generator)

def keep_tags(value, tags):
    """docstring for fname"""
    
    return sanitize_html(value, tags)

def calculate_age(born):
    #Base from : http://stackoverflow.com/a/2259711
    today = date.today()
    if isinstance(born, datetime):
        born = born.date()
    try: # raised when birth date is February 29 and the current year is not a leap year
        birthday = born.replace(year=today.year)
    except ValueError:
        birthday = born.replace(year=today.year, day=born.day-1)
    if birthday > today:
        return today.year - born.year - 1
    else:
        return today.year - born.year