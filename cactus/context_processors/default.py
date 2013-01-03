# coding: utf-8
import os
from cactus.context_processor_base import ContextProcessorBase


class DefaultContextProcessor(ContextProcessorBase):
    def context(self):
        return {
            'CACTUS': {
                'pages': [
                    p for p in self.site.pages() if(
                            p.path.endswith('.html')
                            and
                            os.path.basename(p.path) != "error.html"
                        )
                ]
            }
        }