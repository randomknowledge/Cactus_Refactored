# coding: utf-8


class ContextProcessorBase(object):
    def __init__(self, site):
        self.site = site
        self.name = self.__module__.split(".").pop().replace("context_processors_", "")

    def context(self):
        return {}
