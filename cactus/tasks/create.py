# coding: utf-8
from . import BaseTask


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
