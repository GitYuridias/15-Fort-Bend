# -*- coding: utf-8 -*-
import time, subprocess

try:
    import certifi
except ImportError:
    print('Intalling certifi module')
    subprocess.check_call(["python", '-m', 'pip', 'install', 'certifi'])
    time.sleep(3)

try:
    import urllib3
except ImportError:
    print('Intalling urllib3 module')
    subprocess.check_call(["python", '-m', 'pip', 'install', 'urllib3'])
    time.sleep(3)

try:
    import idna
except ImportError:
    print('Intalling idna module')
    subprocess.check_call(["python", '-m', 'pip', 'install', 'idna'])
    time.sleep(3)

try:
    import chardet
except ImportError:
    print('Intalling chardet module')
    subprocess.check_call(["python", '-m', 'pip', 'install', 'chardet'])
    time.sleep(3)

try:
    import requests
except ImportError:
    print('Intalling requests module')
    subprocess.check_call(["python", '-m', 'pip', 'install', 'requests'])
    time.sleep(3)

try:
    import bs4
except ImportError:
    print('Intalling bs4 module')
    subprocess.check_call(["python", '-m', 'pip', 'install', 'beautifulsoup4'])
    time.sleep(3)

try:
    import jinja2
except ImportError:
    print('Intalling jinja2 module')
    subprocess.check_call(["python", '-m', 'pip', 'install', 'jinja2'])
    time.sleep(3)

from .engine import Engine
from .runner import Runner

__all__ = ['sandbox', 'Runner', 'Engine']
