# coding: utf-8
from . import BaseTask
import cactus


class HelpTask(BaseTask):
    """
    Lorem Ipsum...
    """

    helptext_short = "help <task>: Get help for specified task."

    @classmethod
    def run(cls, *args, **kwargs):
        if len(args) != 1 or not cactus.active_tasks.get(args[0]):
            print cls.usage()
            return
        print cactus.active_tasks.get(args[0]).usage()
