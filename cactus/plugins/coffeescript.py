# coding: utf-8
import shutil
from cactus.utils import fileList, shell_escape, run_subprocess, slitpath
import os
from cactus.plugin_base import CactusPluginBase


class CoffeeScriptPlugin(CactusPluginBase):
    def _path_to_url(self, path, basepath):
        return '/'.join(slitpath(os.path.relpath(path, start=basepath)))

    def postBuild(self, *args, **kwargs):
        self.run()

    def postDist(self, *args, **kwargs):
        self.run(dist=True)

    def run(self, *args, **kwargs):
        from django.conf import settings
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

        output_filename = self.config.get(
            "output_filename",
            "main.js"
        )

        temp_output_filename = ".tmp.main.js"

        coffee = self.config.get(
            "command",
            "coffee --join {output_filename} --compile --output {dir_js} {files}"
        )

        dir_js = os.path.abspath(
            os.path.join(
                self.site.paths["dist" if dist else "build"],
                settings.STATIC_URL_REL, "js"
            )
        )

        cmd = coffee.format(
            output_filename=temp_output_filename,
            dir_js=shell_escape(dir_js),
            files=files,
        )

        result = 0
        if os.name == "nt":
            run_subprocess(cmd)
            # TODO: take return code into account on windows
        else:
            print cmd
            result = os.system(cmd)

        if result == 0:
            shutil.move(
                os.path.abspath(os.path.join(dir_js, temp_output_filename)),
                os.path.abspath(os.path.join(dir_js, output_filename)),
            )
        else:
            try:
                os.remove(os.path.join(dir_js, temp_output_filename))
            except OSError:
                pass
