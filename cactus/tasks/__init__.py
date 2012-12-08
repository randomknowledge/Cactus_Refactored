# coding: utf-8


class BaseTask(object):
    helptext_short = ""

    def __init__(self):
        raise NotImplementedError

    @classmethod
    def help(cls):
        raise NotImplementedError

    @classmethod
    def run(cls, *args, **kwargs):
        raise NotImplementedError

    @classmethod
    def usage(cls):
        return u"\nUsage: cactus {0}\n\n{1}".format(
            cls.helptext_short, cls.__doc__.strip())

    @classmethod
    def name(cls):
        return cls.__module__.split(".").pop()
