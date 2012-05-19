import os
import os.path
import threading
import datetime
import stat
import mimetypes
import logging
import email
import time
import subprocess
import shlex
import hashlib

import tornado.web
from tornado.web import HTTPError
import tornado.ioloop
from tornado import gen

def on_subprocess_result(context, callback, fd, result):    
    try:
        if callback:
            if context.pipe.stderr:
                value = context.pipe.stderr.read()
                if value:
                    logging.error(value)
            callback(context.pipe.stdout)
    except Exception, e:
        logging.error(e)
    finally:
        context.ioloop.remove_handler(fd)

def call_subprocess(context, command, callback=None):
    context.ioloop = tornado.ioloop.IOLoop.instance()
    context.pipe = p = subprocess.Popen(shlex.split(command), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True)
    context.ioloop.add_handler(p.stdout.fileno(), context.async_callback(on_subprocess_result, context, callback), context.ioloop.READ)
    # context.ioloop.add_handler(p.stderr.fileno(), context.async_callback(on_subprocess_result, context, callback), context.ioloop.READ)
