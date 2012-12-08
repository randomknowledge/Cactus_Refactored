# coding: utf-8
from . import BaseTask


class BuildTask(BaseTask):
    """
    Lorem Ipsum...
    """

    helptext_short = "build: Rebuild your site from source files"

    @staticmethod
    def run(*args, **kwargs):
        print "Build called:", args
