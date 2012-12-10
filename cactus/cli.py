#!/usr/bin/env python
# coding: utf-8
import inspect
import traceback
import cactus
from cactus.tasks import BaseTask
from django.utils.log import logger
import re
import os
import sys


def import_tasks():
    imported_tasks = {}
    basedir = os.path.dirname(__file__)
    plugindir = os.path.join(basedir, "tasks")
    parentmodule = "cactus.tasks"
    if os.path.isdir(plugindir):
        for file in os.listdir(plugindir):
            m = re.match(r'^(?P<name>[a-z0-9][a-z0-9_\.-]*)\.py$', file, re.I)
            if m:
                mod = m.group('name')
                try:
                    dsn = "{0}.{1}".format(parentmodule, mod)
                    try:
                        del sys.modules[dsn]
                    except:
                        pass
                    i = __import__(dsn, globals(), locals(),
                                   [parentmodule], -1)
                except Exception:
                    print u"Failed to import Task {0}: {1}".format(
                        mod, traceback.format_exc())
                    logger.error(u"Failed to import Task {0}: {1}".format(
                        mod, traceback.format_exc()))
                else:
                    valid = False
                    for (member_name, member) in inspect.getmembers(i):
                        if (inspect.isclass(member)
                                and member_name != "BaseTask"
                                and issubclass(member, BaseTask)):
                            imported_tasks.update({mod: member})
                            valid = True
                    if not valid:
                        try:
                            del sys.modules[dsn]
                            del i
                        except:
                            pass
    return imported_tasks


def help(tasks):
    usage = "Usage: cactus [{0}]".format("|".join(tasks.keys()))

    print
    print usage
    print

    for name, module in tasks.iteritems():
        print "    {0}".format(module.helptext_short)


def main():
    cactus.active_tasks = import_tasks()
    command = sys.argv[1] if len(sys.argv) > 1 else None
    if not command or not command in cactus.active_tasks.keys():
        help(cactus.active_tasks)
        sys.exit()

    cactus.active_tasks.get(command).run(*sys.argv[2:])

if __name__ == "__main__":
    sys.exit(main())
