# coding: utf-8
import logging
import re
import os
from cactus.utils import fileList
from cactus.plugin_base import CactusPluginBase
from slimit import minify


class MinifyJsPlugin(CactusPluginBase):
    def _minify(self, infile, outfile=None):
        if outfile is None:
            outfile = infile
        logging.info("Minifiing {0}".format(infile))
        f = open(infile, 'r')
        content = f.read()
        f.close()

        f = open(outfile, 'w')
        f.write(minify(content, mangle=False, mangle_toplevel=False))
        f.close()

    def postDist(self, *args, **kwargs):
        buildpath = "dist"
        js_dir = os.path.join(self.site.paths[buildpath], 'static', 'js')
        if not os.path.isdir(js_dir) or not os.listdir(js_dir):
            return

        infile = os.path.abspath(
            os.path.join(
                js_dir,
                'main.js'
            )
        )

        outfile = os.path.abspath(
            os.path.join(
                js_dir,
                self.config.get(
                    'ouput_filename',
                    'main.js'
                )
            )
        )

        self._minify(infile, outfile)

        if infile != outfile and not self.config.get('keep_unminified', True):
            os.remove(infile)

        if self.config.get('minify_vendor_scripts', False):
            for filename in fileList(js_dir):
                if os.path.abspath(filename) != outfile and not re.search(r'\.min\.js$', filename, re.I):
                    self._minify(filename)

        logging.info("done.")

    def templateContext(self, *args, **kwargs):
        return {
            "main_js": self.config.get('ouput_filename', 'main.js')
        }
