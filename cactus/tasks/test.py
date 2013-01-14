# coding: utf-8
import os
import logging
from . import BaseTask


class TestTask(BaseTask):
    helptext_short = "test [test to run]: run the given test or all if no test to run is given."

    @classmethod
    def run(cls, *args, **kwargs):
        test = None
        if len(args) >= 1:
            test = args[0]

        from cactus import site
        site = site.Site(os.getcwd())

        if not kwargs.get("nobuild", False):
            site.build(dist=True)

        if not test:
            logging.info("")
            logging.info("Running all tests...")
            success = True
            for name, test_obj in site._tests.iteritems():
                success &= cls._runtest(name, test_obj)
            return success
        else:
            logging.info("")
            return cls._runtest(test, site._tests[test])

    @classmethod
    def _runtest(cls, name, test):
        logging.info("Running Test '{0}'...".format(name))
        return test.run()

