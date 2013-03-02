# coding: utf-8
import logging
from cactus.utils import fileList, shell_escape, run_subprocess
import os
from cactus.plugin_base import CactusPluginBase


class CoffeeScriptPlugin(CactusPluginBase):
    def _slitpath(self, s):
        rest, tail = os.path.split(s)
        if rest == '':
            return tail,
        return self._slitpath(rest) + (tail,)

    def _path_to_url(self, path, basepath):
        return '/'.join(self._slitpath(os.path.relpath(path, start=basepath)))

    def postBuild(self, *args, **kwargs):
        self.run()

    def postDist(self, *args, **kwargs):
        self.run(dist=True)

    def run(self, *args, **kwargs):
        dist = kwargs.get("dist", False)

        coffeepath = os.path.realpath(
            os.path.join(
                self.site.paths['static'], 'coffee'
            )
        )
        if not os.path.isdir(coffeepath) or not os.listdir(coffeepath):
            return

        def sort_by_buildorder(a, b):
            return 0
        try:
            build_order = self.config.get("build_order")
            if build_order:
                def sort_by_buildorder(a, b):
                    a = self._path_to_url(a, coffeepath)
                    b = self._path_to_url(b, coffeepath)

                    idx_a = 9999999
                    idx_b = 9999999
                    if a in build_order:
                        idx_a = build_order.index(a)

                    if b in build_order:
                        idx_b = build_order.index(b)

                    if idx_a == idx_b:
                        return 0

                    return cmp(idx_a, idx_b)
        except:
            pass

        files = fileList(coffeepath)
        files.sort(sort_by_buildorder)

        files = " ".join(map(lambda x: shell_escape(x), files))
        coffee = self.config.get(
            "command",
            "coffee --join main.js --compile --output {dir_js} {files}"
        )

        cmd = coffee.format(
            dir_js=shell_escape(
                os.path.abspath(
                    os.path.join(
                        self.site.paths["dist" if dist else "build"],
                        "static", "js"
                    )
                )
            ), files=files
        )

        if os.name == "nt":
            run_subprocess(cmd)
        else:
            os.system(cmd)
