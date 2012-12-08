# coding: utf-8
from . import BaseTask


class CreateTask(BaseTask):
    """
    Lorem Ipsum...
    """

    helptext_short = "create: Create a new website skeleton at path"

    @staticmethod
    def run(*args, **kwargs):
        print "Create called:", args
