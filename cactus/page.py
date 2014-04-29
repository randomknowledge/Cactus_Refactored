import BeautifulSoup
import os
import codecs
import logging
from django.template import Template, Context
from .utils import parseValues


class Page(object):
    def __init__(self, site, path):
        self.site = site
        self.path = path
        self._title = None

        self.paths = {
            'full': os.path.join(self.site.path, 'pages', self.path),
            # 'build': os.path.join('.build', self.path),
        }

        user_settings = self.site.config.get('common', {}).get('django_settings', {})
        if not 'STATIC_URL' in user_settings:
            self.url_prefix = '/'.join(
                ['..' for i in xrange(len(self.path.split(os.sep)) - 1)]
            ) or '.'
        else:
            self.url_prefix = ''


    def data(self):
        f = codecs.open(self.paths['full'], 'r', 'utf-8')
        data = f.read()
        f.close()
        return data

    def context(self):
        """
        The page context.
        """

        # Site context
        context = self.site._contextCache

        from django.conf import settings
        static = '{0}{1}'.format(self.url_prefix, settings.STATIC_URL)
        if static.endswith(os.sep):
            static = static[:-1]
        context.update({
            'STATIC_URL': static,
            'ROOT_URL': self.url_prefix,
            'URL': self.path.replace(os.sep, "/"),
        })

        # Page context (parse header)
        context.update(parseValues(self.data())[0])

        return Context(context)

    def gen_template_and_context(self):
        """
        Takes the template data with contect and renders it
        to the final output file.
        """

        data = parseValues(self.data())[1]
        context = self.context()

        # Run the prebuild plugins, we can't use the standard
        # method here because plugins can chain-modify the
        # context and data.
        for plugin in self.site._plugins:
            if hasattr(plugin, 'preBuildPage'):
                context, data = plugin.preBuildPage(
                    self.site, self, context, data
                )

        return Template(data), context

    def render(self):
        """
        Takes the template data with contect and renders it
        to the final output file.
        """

        tpl, ctx = self.gen_template_and_context()
        return tpl.render(ctx)

    def build(self, dist=False):
        """
        Save the rendered output to the output file.
        """
        logging.info("Building %s", self.path)

        data = self.render()

        # Make sure a folder for the output path exists
        try:
            os.makedirs(
                os.path.dirname(
                    os.path.join(
                        self.site.paths["dist" if dist else "build"],
                        self.path
                    )
                )
            )
        except OSError:
            pass

        # Write the data to the output file
        f = codecs.open(
            os.path.join(
                self.site.paths["dist" if dist else "build"],
                self.path
            ),
            'w',
            'utf-8'
        )
        f.write(data)
        f.close()

        # Run all plugins
        #self.site.pluginMethod('postBuildPage',
        #    self.site, self.paths['full-build'])

    def title(self):
        if self._title:
            return self._title

        t = None
        try:
            soup = BeautifulSoup.BeautifulSoup(self.render())
            t = soup.title.string
        except Exception:
            pass

        if not t:
            t, _ = os.path.splitext(os.path.basename(self.path))
            if t.lower() == "index":
                t = os.path.basename(
                    os.path.realpath(
                        os.path.dirname(self.path)
                    )
                )
        self._title = t
        return t

    def url_rel(self):
        return self.path


    def url_abs(self):
        return "/{0}".format(self.path)

    def url(self):
        return self.url_abs()
