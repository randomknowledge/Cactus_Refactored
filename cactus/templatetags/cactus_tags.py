# coding=utf-8
from django.template import Library

register = Library()


def _get_nodelist_recursive(node, nodes=None):
    if nodes is None:
        nodes = []
    nodes.append(node)
    subnodes = getattr(node, 'nodelist', [])
    for subnode in subnodes:
        nodes += _get_nodelist_recursive(subnode, nodes)
    return nodes


@register.simple_tag
def render_block_from_file(from_file, blockname):
    from cactus.templatetags import SITE as site
    for p in site.pages():
        if p.path == "{0}.html".format(from_file):
            tpl, ctx = p.gen_template_and_context()
            for node in tpl:
                for subnode in _get_nodelist_recursive(node):
                    if getattr(subnode, 'name', '') == blockname:
                        return subnode.render(ctx)
    return ""
