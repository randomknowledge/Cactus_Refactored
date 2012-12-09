# coding: utf-8
import logging
import shutil
import socket
import webbrowser
from cactus.page import Page
from cactus.utils import fileList
import os


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

    def bootstrap(self, skeleton):
        """
        Bootstrap a new project at a given path.
        """

        shutil.copytree(skeleton, self.path)

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
            pass

        from .listener import Listener
        from .server import Server, RequestHandler

        self.listener = Listener(self.path, rebuild, ignore=lambda x: '/.build/' in x)
        self.listener.run()
        try:
            httpd = Server(("", port), RequestHandler)
        except socket.error, e:
            logging.info("Could not start webserver, port is in use. To use another port")
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
        #self.loadPlugins()

        #logging.info('Plugins: %s', ', '.join([p.id for p in self._plugins]))

        #self.pluginMethod('preBuild', self, rebuild=rebuild)

        # Make sure the build path exists
        if not os.path.exists(buildpath):
            os.mkdir(buildpath)

        # Copy the static files
        self.build_static()

        # Render the pages to their output files
        map(lambda p: p.build(), self.pages())

        #self.pluginMethod('postBuild', self, rebuild=rebuild)

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
        return {'CACTUS': {'pages': [p for p in self.pages() if p.path.endswith('.html')]}}

    def build_static(self):
        """
        Move static files to build folder. To be fast we symlink it for now,
        but we should actually copy these files in the future.
        """
        staticBuildPath = os.path.join(self.paths['build'], 'static')

        # If there is a folder, replace it with a symlink
        if os.path.lexists(staticBuildPath) and not os.path.exists(staticBuildPath):
            os.remove(staticBuildPath)

        if not os.path.lexists(staticBuildPath):
            shutil.copytree(self.paths['static'], staticBuildPath)
