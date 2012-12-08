# coding: utf-8
from . import BaseTask
import cactus


class HelpTask(BaseTask):
    """
    Lorem Ipsum...
    """

    helptext_short = "help <task>: Get help for specified task."

    @staticmethod
    def run(*args, **kwargs):
        if len(args) != 1 or not cactus.active_tasks[args[0]]:
            print "Usage: cactus help <task>"
            return
        print
        print u"cactus {0}".format(cactus.active_tasks[args[0]].helptext_short)
        print cactus.active_tasks[args[0]].__doc__
