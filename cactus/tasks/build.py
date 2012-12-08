# coding: utf-8
from . import BaseTask


class BuildTask(BaseTask):
    """
    Lorem Ipsum...
    """

    helptext_short = "build: Rebuild your site from source files"

    @classmethod
    def run(cls, *args, **kwargs):
        print "Build called:", args
