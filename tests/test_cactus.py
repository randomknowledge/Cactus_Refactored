import os
import shutil


def create_site(test_dir):
    from cactus.tasks import create
    shutil.rmtree(test_dir, ignore_errors=True)
    create.CreateTask.run(test_dir)
    assert os.path.isdir(test_dir)

def build_site(test_dir):
    from cactus.tasks import build
    os.chdir(test_dir)
    build.BuildTask.run()
    assert os.path.isdir(os.path.realpath(os.path.join(os.getcwd(), "dist")))

def run_plugins(test_dir):
    from cactus.site import Site
    site = Site(test_dir)

    c = open(os.path.join(site.paths['static'], "coffee", "main.coffee"), "w")
    c.write("$ -> console.log 'Cactus Test'")
    c.close()

    c = open(os.path.join(site.paths['static'], "sass", "main.sass"), "w")
    c.write("body\n  background: #000")
    c.close()

    site.load_plugins()
    assert len(site._plugins.keys()) > 0
    site.call_plugin_method("preDist")
    site.call_plugin_method("postDist")

    compressed_js = open(os.path.join(site.paths['dist'], 'static', 'js', 'main.js')).read()
    assert compressed_js.strip() == "(function(){$(function(){return console.log('Cactus Test');});}).call(this);"

    compressed_css = open(os.path.join(site.paths['dist'], 'static', 'css', 'main.css')).read()
    assert compressed_css.strip() == "body{background:#000}"

def test_cactus():
    here = os.getcwd()
    test_dir = os.path.realpath(".tmp/testcactus")
    create_site(test_dir)
    os.chdir(here)
    build_site(test_dir)
    os.chdir(here)
    run_plugins(test_dir)
    os.chdir(here)
