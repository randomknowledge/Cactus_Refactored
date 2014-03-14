# coding: utf-8
from . import BaseTask
import os


class BuildTask(BaseTask):
    """
    """

    helptext_short = "build: Rebuild your site from source files"

    @classmethod
    def run(cls, *args, **kwargs):
        from cactus import site
        site = site.Site(os.getcwd())
        site.build(dist=True)
