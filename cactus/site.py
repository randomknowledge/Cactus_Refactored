# coding: utf-8
import inspect
import logging
from cactus.test_base import CactusTestBase
import django
import re
import shutil
import traceback
import sys
import os
import yaml
import imp
from cactus.page import Page
from cactus.plugin_base import CactusPluginBase
from cactus.context_processor_base import ContextProcessorBase
from cactus.utils import fileList
from cactus import browser
import cactus.templatetags as cactus_tags


class NoCactusDirectoryException(Exception):
    pass


class Site(object):
    def __init__(self, path):
        self.path = path
        self._plugins = {}
        self._context_processors = {}
        self._tests = {}
        self._contextCache = {}
        self.browser = None
        self.plugin_list = []

        self.paths = {
            'build': os.path.join(path, '.tmp'),
            'dist': os.path.join(path, 'dist'),
            'pages': os.path.join(path, 'pages'),
            'templates': os.path.join(path, 'templates'),
            'static': os.path.join(path, 'static'),
            'script': os.path.join(os.getcwd(), __file__)
        }

        if os.path.exists(os.path.join(self.path, "config.yml")):
            self._load_config()

    def _load_config(self):
        try:
            self.config = yaml.load(
                open(os.path.join(self.path, "config.yml"), 'r')
            )

            # Convert plugin commands for windows
            if os.name == 'nt':
                for key, pconf in self.config.get("plugins", {}).iteritems():
                    cmd = pconf.get("command_windows")
                    if cmd:
                        self.config["plugins"][key]["command"] = cmd
                        del self.config["plugins"][key]["command_windows"]
            self.plugin_list = self.config.get("common", {}).get('plugins', {})
        except Exception, e:
            self.config = {}
            logging.warn("Error parsing config.yml:\n{0}".format(e))

    def bootstrap(self, skeleton):
        """
        Bootstrap a new project at a given path.
        """

        shutil.copytree(skeleton, self.path)
        try:
            shutil.move(
                os.path.join(self.path, "_gitignore"),
                os.path.join(self.path, ".gitignore")
            )
        except:
            pass
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

            reload_needed = False
            rebuild_needed = False
            for p in changes.get('any', []):
                if os.path.realpath(os.path.dirname(p)) == os.path.realpath(self.path):
                    if os.path.basename(p) == "config.yml":
                        reload_needed = True
                        rebuild_needed = True
                else:
                    rebuild_needed = True

            if rebuild_needed:
                # We will pause the listener while building so scripts
                # that alter the output like coffeescript and less don't
                # trigger the listener again immediately.
                self.listener.pause()
                try:
                    if reload_needed:
                        self._load_config()
                        self.load_plugins()
                        self.load_context_processors()
                    self.build()
                except Exception, e:
                    logging.info("*** Error while building\n{0}".format(e))
                    traceback.print_exc(file=sys.stdout)

                cssonly = False
                if len(changes["added"]) == 0 and len(changes["deleted"]) == 0:
                    exts = set(map(lambda x: os.path.splitext(x)[1], changes["changed"]))
                    cssonly = True
                    for ext in exts:
                        if not re.match(r'\.(?:css|sass|scss|less)$', ext, re.I):
                            cssonly = False
                if cssonly:
                    browser.browserReloadCSS("http://localhost:{0}".format(port), self)
                else:
                    browser.browserReload("http://localhost:{0}".format(port), self)

                self.listener.resume()

        from .listener import Listener

        self.listener = Listener(
            self.path, rebuild, ignore=lambda x: '/.tmp/' in x
        )
        self.listener.run()

        from twisted.web.server import Site as Website
        from twisted.web.static import File
        from twisted.internet import reactor

        resource = File(self.paths['build'])
        factory = Website(resource)
        reactor.listenTCP(port, factory)

        browser.openurl("http://localhost:{0}".format(port), self)

        try:
            reactor.run()
        except (KeyboardInterrupt, SystemExit):
            reactor.stop()

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

        cactus_tags.register_all(self)

        buildpath = self.paths["dist" if dist else "build"]

        # Set up django settings
        self.setup()

        # Bust the context cache
        self._contextCache = {}

        # Load the plugin code, because we want fresh plugin code on build
        # refreshes if we're running the web server with listen.
        self.load_plugins()
        self.load_context_processors()
        self.load_tests()

        logging.info('Plugins: %s', ', '.join(self._plugins.keys()))
        logging.info('ContextProcessors: %s', ', '.join(self._context_processors.keys()))

        if dist:
            self.call_plugin_method("preDist")
        else:
            self.call_plugin_method("preBuild")

        # Update context from context_processors
        for processor in self._context_processors.values():
            self._contextCache.update(processor.context())

        # Update context from plugins
        self._contextCache.update(self.get_plugin_contexts())

        # Make sure the build path exists
        if not os.path.exists(buildpath):
            os.mkdir(buildpath)

        # Copy the static files
        self.build_static(dist=dist)

        # Render the pages to their output files
        map(lambda p: p.build(dist=dist), self.pages())

        if dist:
            self.call_plugin_method("postDist")
        else:
            self.call_plugin_method("postBuild")

    def setup(self):
        """
        Configure django to use both our template and pages folder as locations
        to look for included templates.
        """
        django_version_16 = float(django.VERSION[0]) + (float(django.VERSION[1]) / 10.0) > 1.5

        default_settings = {
            'STATIC_URL': '/static/',
            'TEMPLATE_DIRS': [self.paths['templates'], self.paths['pages']],
            'INSTALLED_APPS': [] if django_version_16 else ['django.contrib.markup']
        }

        user_settings = self.config.get('common', {}).get('django_settings', {})
        default_settings.update(user_settings)
        if not django_version_16 and not 'django.contrib.markup' in default_settings.get('INSTALLED_APPS'):
            default_settings['INSTALLED_APPS'] = ['django.contrib.markup'] + default_settings['INSTALLED_APPS']

        try:
            from django.conf import settings
            settings.configure(**default_settings)
        except:
            pass

    def pages(self):
        """
        List of pages.
        """
        paths = fileList(self.paths['pages'], relative=True)
        paths = filter(lambda x: not x.endswith("~") and not x.endswith(".haml"), paths)
        return [Page(self, p) for p in paths]

    def build_static(self, dist=False):
        """
        Copy static files to build folder.
        """
        buildpath = self.paths["dist" if dist else "build"]
        s = os.path.join(buildpath, 'static')

        # If there is a folder, replace it with a symlink
        if os.path.exists(s):
            shutil.rmtree(s)

        def ignore_special(src, names):
            bn = os.path.basename(src)
            if bn == "static":
                return self.config.get('build', {}).get('discard_static', [])
            return []

        shutil.copytree(
            self.paths['static'],
            s,
            ignore=ignore_special
        )

        #callable(src, names) -> ignored_names

    def load_plugins(self):
        self._plugins = self.load_modules("plugins", CactusPluginBase)

    def load_context_processors(self):
        self._context_processors = self.load_modules("context_processors", ContextProcessorBase)

    def load_tests(self):
        self._tests = self.load_modules("tests", CactusTestBase)

    def load_modules(self, module_type, baseclass):
        imported_modules = {}

        local_modules_dir = os.path.realpath(
            os.path.join(self.path, module_type)
        )
        global_modules_dir = os.path.realpath(
            os.path.join(os.path.dirname(__file__), module_type)
        )
        modules_to_load = None

        try:
            modules_to_load = self.config.get("common").get(module_type, [])
        except:
            pass

        if modules_to_load:
            for module in modules_to_load:
                path = os.path.realpath(
                    os.path.join(local_modules_dir, "{0}.py".format(module))
                )
                if not os.path.exists(path):
                    path = os.path.realpath(
                        os.path.join(
                            global_modules_dir, "{0}.py".format(module)
                        )
                    )

                try:
                    i = imp.load_source('%s_%s' % (module_type, module), path)
                except Exception:
                    logging.error(u"Failed to import Module {0}: {1}".format(
                        module, traceback.format_exc())
                    )
                else:
                    for (member_name, member) in inspect.getmembers(i):
                        if (inspect.isclass(member) and
                            member_name != baseclass.__name__
                            and issubclass(member, baseclass)):
                            imported_modules.update({module: member(self)})
        return imported_modules


    def call_plugin_method(self, method, *args, **kwargs):
        """
        Run this method on all plugins
        """
        cwd = os.getcwd()
        self.load_plugins()

        for plugin_name in self.plugin_list:
            plugin = self._plugins.get(plugin_name, None)
            if plugin:
                if hasattr(plugin, method):
                    getattr(plugin, method)(*args, **kwargs)
        os.chdir(cwd)

    def get_plugin_contexts(self, *args, **kwargs):
        if not hasattr(self, '_plugins'):
            self.load_plugins()
        ctx = {}
        for plugin_name, plugin in self._plugins.iteritems():
            if hasattr(plugin, "templateContext"):
                ctx[plugin_name] = plugin.templateContext(*args, **kwargs)
        return {
            "plugins": ctx
        }


    def run_tests(self):
        success = True
        for test_obj in self._tests.values():
            success &= test_obj.run()
        return success
