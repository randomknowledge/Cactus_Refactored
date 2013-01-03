import BeautifulSoup
import os
import codecs
import logging

from .utils import parseValues

from django.template import Template, Context, loader


class Page(object):
    def __init__(self, site, path):
        self.site = site
        self.path = path
        self._title = None

        self.paths = {
            'full': os.path.join(self.site.path, 'pages', self.path),
            # 'build': os.path.join('.build', self.path),
        }

        self.url_prefix = '/'.join(
            ['..' for i in xrange(len(self.path.split(os.sep)) - 1)]
        ) or '.'


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

        context.update({
            'STATIC_URL': '{0}/static'.format(self.url_prefix),
            'ROOT_URL': self.url_prefix,
            'URL': self.path.replace(os.sep, "/"),
        })

        # Page context (parse header)
        context.update(parseValues(self.data())[0])

        return Context(context)

    def render(self):
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

        return Template(data).render(context)

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