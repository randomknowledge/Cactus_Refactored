# coding: utf-8


class CactusPluginBase(object):
    def __init__(self, site):
        self.site = site

    def preBuild(self, *args, **kwargs):
        pass

    def preDist(self, *args, **kwargs):
        pass

    def postBuild(self, *args, **kwargs):
        pass

    def postDist(self, *args, **kwargs):
        pass

    def preDeploy(self, *args, **kwargs):
        pass

    def postDeploy(self, *args, **kwargs):
        pass
