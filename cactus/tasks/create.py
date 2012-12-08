# coding: utf-8
from . import BaseTask
import sys
import os


class CreateTask(BaseTask):
    """
    Creates a new project at the given path.
    """

    helptext_short = "create <path>: Create a new website skeleton at path"

    @classmethod
    def run(cls, *args, **kwargs):
        if len(args) != 1:
            print cls.usage()
            return
        path = os.path.realpath(args[0])
        if os.path.exists(path):
            print "Path {0} already exists!".format(path)
            sys.exit()

        os.makedirs(path)
        project_name = os.path.basename(path)

        from cactus import site
        site = site.Site(path)
        site.bootstrap()

        print u"Project '{0}' created in '{1}'.".format(project_name, path)
