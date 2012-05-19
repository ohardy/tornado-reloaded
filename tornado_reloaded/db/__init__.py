#!/usr/bin/env python
# -*- coding: utf-8 -*-
# encoding: utf-8
"""
db.py

Created by Olivier Hardy on 2012-01-04.
Copyright (c) 2011 Olivier Hardy. All rights reserved.
"""

import logging
from threading import Condition

APYMONGO_ENABLED = False

try:
    import apymongo
except:
    pass
else:
    APYMONGO_ENABLED = True

from tornado.options import options

from loading import db

condition = Condition()

def get_db():
    """docstring for get_db"""
    condition.acquire()
    db = None
    if 1:
        try:
            if APYMONGO_ENABLED and options.databases.get('default', False) and options.databases['default']['backend'] == 'mongodb' and options.databases['default']['database_name']:
                db = apymongo.Connection()[options.databases['default']['database_name']]
        except Exception as e:
            logging.exception(e)
        finally:
            condition.release()
    
    return db