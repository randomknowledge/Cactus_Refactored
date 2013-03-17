# coding: utf-8
import os
import codecs
import logging
from cactus.plugin_base import CactusPluginBase
from cactus.utils import fileList
from hamlpy.hamlpy import Compiler


class HamlPlugin(CactusPluginBase):
    def postBuild(self, *args, **kwargs):
        self.cleanup()

    def postDist(self, *args, **kwargs):
        self.cleanup()

    def preBuild(self, *args, **kwargs):
        self.run()

    def preDist(self, *args, **kwargs):
        self.run()

    def files(self):
        return filter(
            lambda f: f.endswith('.haml'),
            fileList(self.site.paths['templates']) + fileList(self.site.paths['pages'])
        )

    def run(self, *args, **kwargs):
        for haml in self.files():
            haml_lines = codecs.open(haml, 'r', encoding='utf-8').read().splitlines()
            compiler = Compiler()
            output = compiler.process_lines(haml_lines)
            html = haml.replace('.haml', '.html')
            logging.info("[HAML] Compiling {0} -> {1}...".format(haml, html))
            with open(html, 'w') as f:
                f.write(output)

    def cleanup(self):
        for haml in self.files():
            html = haml.replace('.haml', '.html')
            try:
                os.remove(html)
            except:
                pass
