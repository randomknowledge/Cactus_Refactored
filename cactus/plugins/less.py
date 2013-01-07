# coding: utf-8
from cactus.utils import shell_escape, run_subprocess
import os
from cactus.plugin_base import CactusPluginBase


class LessPlugin(CactusPluginBase):
    def postBuild(self, *args, **kwargs):
        self.run()

    def postDist(self, *args, **kwargs):
        self.run(dist=True)

    def run(self, *args, **kwargs):
        dist = kwargs.get("dist", False)
        buildpath = "dist" if dist else "build"
        less_dir = os.path.join(self.site.paths['static'], "less")
        css_dir = os.path.join(self.site.paths[buildpath], 'static', 'css')
        if not os.path.isdir(less_dir) or not os.listdir(less_dir):
            return

        main_file_less = self.config.get("main_file_less", "main.less")
        main_file_css = self.config.get("main_file_css", "main.css")
        sass = self.config.get(
            "command",
            "lessc {input} {output}"
        )

        cmd = sass.format(
            input=shell_escape(
                os.path.realpath(
                    os.path.join(less_dir, main_file_less)
                )
            ),
            output=shell_escape(
                os.path.realpath(
                    os.path.join(css_dir, main_file_css)
                )
            ),
            )

        os.chdir(less_dir)
        if os.name == "nt":
            run_subprocess(cmd)
        else:
            os.system(cmd)
