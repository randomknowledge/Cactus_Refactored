# coding: utf-8
from . import BaseTask


class ServeTask(BaseTask):
    """
    Lorem Ipsum...
    """

    helptext_short = "serve [host:port]: Serve you website at " \
                     "local development server"

    @classmethod
    def run(cls, *args, **kwargs):
        print "Serve called:", args
