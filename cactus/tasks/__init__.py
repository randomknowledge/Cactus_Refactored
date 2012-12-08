# coding: utf-8


class BaseTask(object):
    helptext_short = ""

    def __init__(self):
        raise NotImplementedError

    @staticmethod
    def help():
        raise NotImplementedError

    @staticmethod
    def run(*args, **kwargs):
        raise NotImplementedError
