# coding=utf-8
import re
import os
from django.template.loader import add_to_builtins


re_validfile = re.compile(r'^(?P<name>[a-z][a-z0-9_-]*)\.py$', re.I)
SITE = None


def register_all(site):
    global SITE
    SITE = site
    basedir = os.path.dirname(__file__)
    for libname in os.listdir(basedir):
        match = re_validfile.search(libname)
        if match:
            add_to_builtins('cactus.templatetags.{0}'.format(match.group('name')))
