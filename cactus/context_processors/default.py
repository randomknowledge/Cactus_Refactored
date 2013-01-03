# coding: utf-8
from cactus.utils import template_escape_path
import os
from cactus.context_processor_base import ContextProcessorBase


class DefaultContextProcessor(ContextProcessorBase):
    def context(self):
        pages = [
            p for p in self.site.pages() if(
                p.path.endswith('.html')
                and
                os.path.basename(p.path) != "error.html"
                )
        ]

        pages_by_path = {}
        for p in pages:
            pages_by_path[template_escape_path(p.path)] = p

        return {
            'CACTUS': {
                'pages': pages,
                'pages_by_path': pages_by_path
            }
        }