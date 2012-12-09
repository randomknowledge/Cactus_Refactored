# coding: utf-8
import shutil
import os


class NoCactusDirectoryException(Exception):
    pass


class Site(object):
    def __init__(self, path):
        self.path = path

    def bootstrap(self, skeleton):
        """
        Bootstrap a new project at a given path.
        """

        shutil.copytree(skeleton, self.path)

    def verify(self):
        """
        Check if this path looks like a Cactus website
        """

        for p in ['pages', 'static', 'templates']:
            if not os.path.isdir(os.path.join(self.path, p)):
                raise NoCactusDirectoryException(
                    "missing '{0}' subfolder".format(p))

    def serve(self, uri="localhost:8000"):
        """
        Start a http server and rebuild on changes.
        """
        print "SERVE"
