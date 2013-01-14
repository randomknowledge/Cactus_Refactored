# coding: utf-8
import logging
import re
import os
from cactus.test_base import CactusTestBase


class ConsoleLogTest(CactusTestBase):
    def run(self):
        basedir = self.site.paths['dist']
        found = []
        for (path, dirs, files) in os.walk(basedir):
            for file in files:
                if file.lower().endswith(".js"):
                    lineno = 0
                    f = os.path.join(path, file)
                    for line in open(f,'r'):
                        lineno += 1
                        if re.search(r'console\.log', line, re.I):
                            found.append({
                                "file": f,
                                "line": lineno,
                                "content": line,
                            })
        if found:
            logging.warn("==========================================================================")
            logging.warn("Found {0} console.log statements:".format(len(found)))
            for l in found:
                logging.warn("{0}:{1}".format(l.get("file"), l.get("line")))
                logging.warn(l.get("content"))
            logging.warn("==========================================================================")
            return False
        return True