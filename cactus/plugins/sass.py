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
        from django.conf import settings
        s_type = self.config.get("type", "sass")
        if s_type != "sass" and s_type != "scss":
            s_type = "sass"

        dist = kwargs.get("dist", False)
        buildpath = "dist" if dist else "build"
        sass_dir = os.path.join(self.site.paths['static'], s_type)
        css_dir = os.path.join(self.site.paths[buildpath], settings.STATIC_URL_REL, 'css')
        if not os.path.isdir(sass_dir) or not os.listdir(sass_dir):
            return

        if not os.path.exists(css_dir):
            os.makedirs(css_dir)

        main_file_sass = self.config.get("main_file_sass", "main.sass")
        if s_type == "scss":
            main_file_sass = self.config.get("main_file_scss", "main.scss")
        main_file_css = self.config.get("main_file_css", "main.css")
        sass = self.config.get(
            "command",
            "%s -t compressed {input} {output}" % s_type
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
