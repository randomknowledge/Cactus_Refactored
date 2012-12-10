# coding: utf-8
import logging
import re
import os
from cactus.utils import fileList
from cactus.plugin_base import CactusPluginBase
from slimit import minify


class SassPlugin(CactusPluginBase):
    def postDist(self, *args, **kwargs):
        buildpath = "dist"
        js_dir = os.path.join(self.site.paths[buildpath], 'static', 'js')
        if not os.path.isdir(js_dir) or not os.listdir(js_dir):
            return

        for file in fileList(js_dir):
            if re.search(r'main\.js$', file, re.I):
                logging.info("Minifiing {0}".format(file))
                f = open(file, 'r')
                content = f.read()
                f.close()

                f = open(file, 'w')
                f.write(minify(content, mangle=False, mangle_toplevel=False))
                f.close()
                logging.info("done.")
