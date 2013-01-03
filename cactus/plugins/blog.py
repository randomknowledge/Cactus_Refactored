# coding: utf-8
import glob
from cactus.page import Page
import os
from cactus.plugin_base import CactusPluginBase


class BlogPlugin(CactusPluginBase):
    def templateContext(self, *args, **kwargs):
        posts_path = os.path.abspath(
            os.path.join(
                self.site.paths['pages'],
                self.config.get("post_identifier")
            )
        )

        pages_ctx = {"posts": []}
        for post in glob.glob(posts_path):
            post_rel = post.split(os.sep)
            i = -1
            while os.path.abspath(os.sep.join(post_rel[:i])) != os.path.abspath(self.site.paths['pages']):
                i -= 1
                if -i >= len(post_rel):
                    break
            post_url = "/".join(post_rel[i:])
            pages_ctx["posts"].append({
                "url": "/" + post_url,
                "url_rel": post_url,
                "title": Page(self.site, post).title()
            })

        return pages_ctx
