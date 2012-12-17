# coding: utf-8
import os
from . import BaseTask


class ServeTask(BaseTask):
    helptext_short = "serve [listen_address:port]: Serve you website at " \
                     "local development server"

    @classmethod
    def run(cls, *args, **kwargs):
        uri = "0.0.0.0:8000"
        if len(args) >= 1:
            uri = args[0]

        from cactus import site
        site = site.Site(os.getcwd())
        site.verify()
        site.serve(uri=uri)
