# coding: utf-8


class CactusPluginBase(object):
    def __init__(self, site):
        self.site = site
        self.name = self.__module__.split(".").pop().replace("plugin_", "")
        try:
            self.config = site.config.get("plugins").get(self.name)
        except:
            pass
        if not self.config:
            self.config = {}

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

    def templateContext(self, *args, **kwargs):
        return {}
