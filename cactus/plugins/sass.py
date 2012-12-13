# coding: utf-8
from cactus.utils import shell_escape, run_subprocess
import os
from cactus.plugin_base import CactusPluginBase


class SassPlugin(CactusPluginBase):
    def postBuild(self, *args, **kwargs):
        self.run()

    def postDist(self, *args, **kwargs):
        self.run(dist=True)

    def run(self, *args, **kwargs):
        dist = kwargs.get("dist", False)
        buildpath = "dist" if dist else "build"
        sass_dir = os.path.join(self.site.paths['static'], 'sass')
        css_dir = os.path.join(self.site.paths[buildpath], 'static', 'css')
        if not os.path.isdir(sass_dir) or not os.listdir(sass_dir):
            return

        main_file_sass = self.config.get("main_file_sass", "main.sass")
        main_file_css = self.config.get("main_file_css", "main.css")
        sass = self.config.get(
            "command",
            "sass -t compressed {input} {output}"
        )

        cmd = sass.format(
            input=shell_escape(
                os.path.realpath(
                    os.path.join(sass_dir, main_file_sass)
                )
            ),
            output=shell_escape(
                os.path.realpath(
                    os.path.join(css_dir, main_file_css)
                )
            ),
        )

        os.chdir(sass_dir)
        if os.name == "nt":
            run_subprocess(cmd)
        else:
            os.system(cmd)
