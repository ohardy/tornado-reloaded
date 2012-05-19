#!/usr/bin/env python
#
# Copyright 2009 Facebook
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import distutils.core
from setuptools import setup
import sys
# Importing setuptools adds some features like "setup.py develop", but
# it's optional so swallow the error if it's not there.
try:
    import setuptools
except ImportError:
    pass

kwargs = {}

# Build the epoll extension for Linux systems with Python < 2.6
extensions = []
major, minor = sys.version_info[:2]
python_26 = (major > 2 or (major == 2 and minor >= 6))

version = "1.2"

if major >= 3:
    import setuptools  # setuptools is required for use_2to3
    kwargs["use_2to3"] = True

console_scripts = [
    'tornado = tornado_reloaded.management.handler:execute',
]

setup(
    name="tornado_reloaded",
    version=version,
    packages = ["tornado_reloaded"],
    package_data = {},
    ext_modules = extensions,
    install_requires=["skeleton"],
    author="Facebook",
    author_email="ohardy@me.com",
    url="https://github.com/ohardy/tornado-reloaded",
    download_url="https://github.com/ohardy/tornado-reloaded",
    license="http://www.apache.org/licenses/LICENSE-2.0",
    description="Tornado-reloaded",
    entry_points        =   {
        'console_scripts': console_scripts,
    },
    **kwargs
)
