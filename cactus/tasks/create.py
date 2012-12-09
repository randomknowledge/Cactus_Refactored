# coding: utf-8
from . import BaseTask
import re
import sys
import os


class CreateTask(BaseTask):
    """
    Creates a new project at the given path.
    Optionally provide a skeleton name or path.
    """

    helptext_short = "create <path> [<skeleton type>|<skeleton path>]: " \
                     "Create a new website skeleton at path"

    @classmethod
    def run(cls, *args, **kwargs):
        if len(args) < 1 or len(args) > 2:
            print cls.usage()
            return
        path = os.path.realpath(args[0])
        skel = "default"
        if len(args) == 2:
            skel = args[1]
        if not re.search(r'[\/]', skel):
            skel = os.path.realpath(
                os.path.join(
                    os.path.dirname(__file__), "..", "skeletons", skel
                )
            )
        if not os.path.isdir(skel):
            print "No skeleton found at {0}".format(skel)
            sys.exit()

        if os.path.exists(path):
            print "Path {0} already exists!".format(path)
            sys.exit()

        #os.makedirs(path)
        project_name = os.path.basename(path)

        from .. import site
        site = site.Site(path)
        site.bootstrap(skel)

        print u"Project '{0}' created in '{1}'.".format(project_name, path)
