# coding: utf-8
import shutil
import os
import codecs
import logging
from cactus.plugin_base import CactusPluginBase
from cactus.utils import fileList, run_subprocess
from hamlpy.hamlpy import Compiler


class CssSpritesPlugin(CactusPluginBase):
    def postBuild(self, *args, **kwargs):
        self.run()

    def postDist(self, *args, **kwargs):
        self.run(dist=True)

    def _convert_dir(self, c_dir, basedir):
        return os.path.abspath(
            os.path.join(
                basedir,
                c_dir
            )
        )

    def run(self, *args, **kwargs):
        outformat = "css"
        if "sass" in self.site._plugins:
            outformat = "sass"
        elif "less" in self.site._plugins:
            outformat = "less"

        dist = kwargs.get("dist", False)
        input_dir = self.config.get('input_dir', 'img/_sprites')
        output_dir = self.config.get('output_dir', 'img/sprites')
        css_dir = self.config.get('css_dir', 'css/sprites')
        if outformat != "css":
            css_dir = "{0}/sprites".format(outformat)
        dont_deploy_input_dir = self.config.get('dont_deploy_input_dir', True)
        retina = self.config.get('retina', False)
        format_param = ' --format={0}'.format(outformat)
        command = self.config.get(
            'command',
            'glue --cachebuster --crop {retina} {input_dir} --css={css_dir} --img={output_dir}'
        )

        command += format_param

        basedir = os.path.abspath(
            os.path.join(
                self.site.paths['dist' if dist else 'build'],
                'static'
            )
        )
        staticdir = os.path.abspath(self.site.paths['static'])
        route_img_dir = "../{0}".format(os.path.normpath(output_dir))
        input_dir = self._convert_dir(input_dir, basedir)
        output_dir = self._convert_dir(output_dir, basedir)
        if outformat == "css":
            css_dir = self._convert_dir(css_dir, basedir)
        else:
            css_dir = self._convert_dir(css_dir, staticdir)
            command += " --route-img={0}".format(route_img_dir)

        if not os.path.exists(input_dir):
            logging.info("No CSS Sprites to generate.")
            return

        for sprite in os.listdir(input_dir):
            sprite_dir = os.path.abspath(
                os.path.join(input_dir, sprite)
            )
            if os.path.isdir(sprite_dir):
                cmd = command.format(
                    retina='--retina' if retina else '',
                    input_dir=sprite_dir,
                    css_dir=css_dir,
                    output_dir=output_dir,
                )
                logging.info("Generating Sprite '{0}'...".format(sprite))
                logging.info(cmd)

                if os.name == "nt":
                    run_subprocess(cmd)
                else:
                    os.system(cmd)
                """
                if sass:
                    if not os.path.exists(sass_dir):
                        os.makedirs(sass_dir)
                    sass_out = os.path.join(
                        sass_dir,
                        "{0}.{1}".format(sprite, sass_type)
                    )
                    sass_cmd = sass_convert_command.format(
                        in_format='css',
                        out_format=sass_type,
                        infile=os.path.join(
                            css_dir,
                            "{0}.css".format(sprite)
                        ),
                        outfile=sass_out,
                    )
                    if os.name == "nt":
                        run_subprocess(sass_cmd)
                    else:
                        os.system(sass_cmd)
                    sass_content = open(sass_out, 'r').read().replace("'../../", "'../")
                    f = open(sass_out, 'w')
                    f.write(sass_content)
                    f.close()

                    shutil.rmtree(css_dir, ignore_errors=True)
                """
        if dont_deploy_input_dir:
            shutil.rmtree(input_dir, ignore_errors=True)
