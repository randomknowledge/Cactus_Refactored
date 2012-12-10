# coding: utf-8
import re
import os
from cactus.utils import shell_escape, fileList
from cactus.plugin_base import CactusPluginBase


re_optipng = re.compile(r'\.(?:png|gif)$', re.I)
re_jpegoptim = re.compile(r'\.jpe?g$', re.I)

class ImageOptiPlugin(CactusPluginBase):
    def postDist(self, *args, **kwargs):

        files = fileList(os.path.join(self.site.paths['dist'], 'static'))

        def filter_png(f):
            return bool(re_optipng.search(f))

        def filter_jpg(f):
            return bool(re_jpegoptim.search(f))

        optipng = self.config.get(
            "command_png",
            "optipng {files}"
        )

        jpegoptim = self.config.get(
            "command_jpg",
            "jpegoptim -o -t --strip-all {file}"
        )

        pngs = map(lambda x: shell_escape(x), filter(filter_png, files))
        if pngs:
            command = optipng.format(files=" ".join(pngs))
            os.system(command)

        for f in filter(filter_jpg, files):
            command = jpegoptim.format(file=f)
            os.system(command)
