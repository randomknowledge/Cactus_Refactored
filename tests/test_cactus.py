import os
import shutil

def test_foo():
    assert True

def test_cactus():
    from cactus.tasks import create, build

    test_dir = ".tmp/testcactus"
    here = os.getcwd()

    shutil.rmtree(test_dir, ignore_errors=True)
    create.CreateTask.run(test_dir)
    assert os.path.isdir(test_dir)
    os.chdir(test_dir)
    build.BuildTask.run()
    assert os.path.isdir(os.path.realpath(os.path.join(os.getcwd(), "dist")))
    os.chdir(here)
