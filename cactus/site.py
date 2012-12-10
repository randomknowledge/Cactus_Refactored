# coding: utf-8
import inspect
import logging
import shutil
import socket
import traceback
import webbrowser
import sys
import os
import yaml
from cactus.page import Page
from cactus.plugin_base import CactusPluginBase
from cactus.utils import fileList
from cactus import browser


class NoCactusDirectoryException(Exception):
    pass


class Site(object):
    def __init__(self, path):
        self.path = path
        self._plugins = []

        self.paths = {
            'build': os.path.join(path, '.tmp'),
            'dist': os.path.join(path, 'dist'),
            'pages': os.path.join(path, 'pages'),
            'templates': os.path.join(path, 'templates'),
            'static': os.path.join(path, 'static'),
            'script': os.path.join(os.getcwd(), __file__)
        }

        self._load_config()

    def _load_config(self):
        try:
            self.config = yaml.load(open(os.path.join(self.path, "config.yml"), 'r'))
        except:
            self.config = {}

    def bootstrap(self, skeleton):
        """
        Bootstrap a new project at a given path.
        """

        shutil.copytree(skeleton, self.path)
        self._load_config()

    def verify(self):
        """
        Check if this path looks like a Cactus website
        """

        for p in ['pages', 'static', 'templates']:
            if not os.path.isdir(os.path.join(self.path, p)):
                raise NoCactusDirectoryException(
                    "missing '{0}' subfolder".format(p))

    def serve(self, uri="localhost:8000"):
        """
        Start a http server and rebuild on changes.
        """
        host, _, port = uri.partition(":")
        port = int(port)

        self.clean()
        self.build(dist=False)

        logging.info('Running webserver at {0}'.format(uri))
        logging.info('Type control-c to exit')

        os.chdir(self.paths['build'])

        def rebuild(changes):
            logging.info("*** Rebuilding ({0} changed)".format(self.path))

            # We will pause the listener while building so scripts that alter the output
            # like coffeescript and less don't trigger the listener again immediately.
            self.listener.pause()
            try:
                self.build()
            except Exception, e:
                logging.info("*** Error while building\n{0}".format(e))
                traceback.print_exc(file=sys.stdout)

            browser.browserReload("http://localhost:{0}".format(port))

            self.listener.resume()


        from .listener import Listener
        from .server import Server, RequestHandler

        self.listener = Listener(
            self.path, rebuild, ignore=lambda x: '/.build/' in x
        )
        self.listener.run()
        try:
            httpd = Server(("", port), RequestHandler)
        except socket.error:
            logging.info("Could not start webserver, port is in use.")
            return
        webbrowser.open("http://localhost:{0}".format(port))

        try:
            httpd.serve_forever()
        except (KeyboardInterrupt, SystemExit):
            httpd.server_close()

        logging.info('See you!')

    def clean(self):
        """
        Remove all build files.
        """
        if os.path.isdir(self.paths['build']):
            shutil.rmtree(self.paths['build'])

    def build(self, dist=False):
        """
        Generate fresh site from templates.
        """

        buildpath = self.paths["dist" if dist else "build"]

        # Set up django settings
        self.setup()

        # Bust the context cache
        self._contextCache = self.context()

        # Load the plugin code, because we want fresh plugin code on build
        # refreshes if we're running the web server with listen.
        self.load_plugins()

        logging.info('Plugins: %s', ', '.join(self._plugins.keys()))

        self.call_plugin_method("preBuild")

        # Make sure the build path exists
        if not os.path.exists(buildpath):
            os.mkdir(buildpath)

        # Copy the static files
        self.build_static()

        # Render the pages to their output files
        map(lambda p: p.build(), self.pages())
        self.call_plugin_method("postBuild")

    def setup(self):
        """
        Configure django to use both our template and pages folder as locations
        to look for included templates.
        """
        try:
            from django.conf import settings
            settings.configure(
                TEMPLATE_DIRS=[self.paths['templates'], self.paths['pages']],
                INSTALLED_APPS=['django.contrib.markup']
            )
        except:
            pass

    def pages(self):
        """
        List of pages.
        """
        paths = fileList(self.paths['pages'], relative=True)
        paths = filter(lambda x: not x.endswith("~"), paths)
        return [Page(self, p) for p in paths]

    def context(self):
        """
        Base context for the site: all the html pages.
        """
        return {
            'CACTUS': {
                'pages': [
                    p for p in self.pages() if p.path.endswith('.html')
                ]
            }
        }

    def build_static(self):
        """
        Move static files to build folder. To be fast we symlink it for now,
        but we should actually copy these files in the future.
        """
        s = os.path.join(self.paths['build'], 'static')

        # If there is a folder, replace it with a symlink
        if os.path.lexists(s) and not os.path.exists(s):
            os.remove(s)

        if not os.path.lexists(s):
            shutil.copytree(self.paths['static'], s)

    def load_plugins(self):
        imported_plugins = {}

        local_plugin_dir = os.path.realpath(
            os.path.join(self.path, "plugins")
        )
        global_plugin_dir = os.path.realpath(
            os.path.join(os.path.dirname(__file__), "plugins")
        )
        parentmodule = "cactus.plugins"
        for plugin in self.config.get("common").get("plugins"):
            path = os.path.realpath(
                os.path.join(local_plugin_dir, "{0}.py".format(plugin))
            )
            if not os.path.exists(path):
                path = os.path.realpath(
                    os.path.join(global_plugin_dir, "{0}.py".format(plugin))
                )
            dsn = "{0}.{1}".format(parentmodule, plugin)
            try:
                del sys.modules[dsn]
            except:
                pass
            try:
                i = __import__(dsn, globals(), locals(), [parentmodule], -1)
            except Exception:
                logging.error(u"Failed to import Plugin {0}: {1}".format(
                    plugin, traceback.format_exc())
                )
            else:
                valid = False
                for (member_name, member) in inspect.getmembers(i):
                    if inspect.isclass(member)\
                    and member_name != "CactusPluginBase"\
                    and issubclass(member, CactusPluginBase):
                        valid = True
                        imported_plugins.update({plugin: member(self)})
                if not valid:
                    try:
                        del sys.modules[dsn]
                        del i
                    except:
                        pass
        self._plugins = imported_plugins

    def call_plugin_method(self, method, *args, **kwargs):
        """
        Run this method on all plugins
        """

        if not hasattr(self, '_plugins'):
            self.load_plugins()

        for plugin_name, plugin in self._plugins.iteritems():
            if hasattr(plugin, method):
                getattr(plugin, method)(*args, **kwargs)
