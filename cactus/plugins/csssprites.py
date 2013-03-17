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
        dist = kwargs.get("dist", False)
        input_dir = self.config.get('input_dir', 'img/_sprites')
        output_dir = self.config.get('output_dir', 'img/sprites')
        css_dir = self.config.get('css_dir', 'css/sprites')
        dont_deploy_input_dir = self.config.get('dont_deploy_input_dir', True)
        retina = self.config.get('retina', False)
        command = self.config.get(
            'command',
            'glue --cachebuster --crop {retina} {input_dir} --css={css_dir} --img={output_dir}'
        )

        basedir = os.path.abspath(
            os.path.join(
                self.site.paths['dist' if dist else 'build'],
                'static'
            )
        )

        input_dir = self._convert_dir(input_dir, basedir)
        output_dir = self._convert_dir(output_dir, basedir)
        css_dir = self._convert_dir(css_dir, basedir)

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
        if dont_deploy_input_dir:
            shutil.rmtree(input_dir, ignore_errors=True)