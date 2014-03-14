# coding: utf-8
import logging
import re
import os
import shutil
from cactus.utils import fileList
from cactus.plugin_base import CactusPluginBase
from slimit import minify


class MinifyJsPlugin(CactusPluginBase):
    infile = None
    outfile = None
    buildpath = None
    js_dir = None

    def _prepare(self, *args, **kwargs):
        from django.conf import settings
        dist = kwargs.get("dist", False)
        self.buildpath = "dist" if dist else "build"
        self.js_dir = os.path.join(self.site.paths[self.buildpath], settings.STATIC_URL_REL, 'js')
        if not os.path.isdir(self.js_dir) or not os.listdir(self.js_dir):
            return False

        self.infile = os.path.abspath(
            os.path.join(
                self.js_dir,
                self.config.get(
                    'input_filename',
                    'main.js'
                )
            )
        )

        self.outfile = os.path.abspath(
            os.path.join(
                self.js_dir,
                self.config.get(
                    'ouput_filename',
                    'main.js'
                )
            )
        )

        return True

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

    def postBuild(self, *args, **kwargs):
        if not self._prepare(dist=False):
            return

        # Do not minify in devlopment mode, only rename file
        try:
            shutil.move(self.infile, self.outfile)
        except IOError:
            pass

    def postDist(self, *args, **kwargs):
        if not self._prepare(dist=True):
            return

        self._minify(self.infile, self.outfile)

        if self.infile != self.outfile and not self.config.get('keep_unminified', True):
            os.remove(self.infile)

        if self.config.get('minify_vendor_scripts', False):
            for filename in fileList(self.js_dir):
                if os.path.abspath(filename) != self.outfile and not re.search(r'\.min\.js$', filename, re.I):
                    self._minify(filename)

        logging.info("done.")

    def templateContext(self, *args, **kwargs):
        return {
            "main_js": self.config.get('ouput_filename', 'main.js')
        }
