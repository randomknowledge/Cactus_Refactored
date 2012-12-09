# coding: utf-8
import pipes
import subprocess
from cactus.utils import fileList, shell_escape
import os
from cactus.plugins import CactusPluginBase


class CoffeeScriptPlugin(CactusPluginBase):
    def postBuild(self, *args, **kwargs):
        self.run()

    def postDist(self, *args, **kwargs):
        self.run()

    def run(self, *args, **kwargs):
        coffeepath = os.path.realpath(
            os.path.join(
                self.site.paths['build'], 'static', 'coffee'
            )
        )
        if not os.path.isdir(coffeepath) or not os.listdir(coffeepath):
            return

        #os.chdir(os.path.join( self.site.paths['build'], 'static'))

        def sort_by_buildorder(a, b):
            return 0
        try:
            build_order = self.site.config.get("coffee").get("build_order")
            if build_order:
                def sort_by_buildorder(a, b):
                    a = a.replace(coffeepath + "/", "")
                    b = b.replace(coffeepath + "/", "")
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
        coffee = "coffee"
        #TODO: make this configurable
        if os.name == "nt":
            coffee = '"c:/Program Files/nodejs/node.exe" ' \
                     '"c:/Program Files/CoffeeScript/bin/coffee"'
        cmd = "{0} --join main.js --compile " \
              "--output {1} {2}".format(
                    coffee,
                    shell_escape(
                        os.path.abspath(
                            os.path.join(
                                self.site.paths['build'], "static", "js"
                            )
                        )
                    ), files
        )

        if os.name == "nt":
            subprocess.check_output(cmd, shell=True)
        else:
            os.system(cmd)
