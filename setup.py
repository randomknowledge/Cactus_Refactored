# coding: utf-8
"""
Cactus

Static site generation and deployment.

:copyright: (c) 2012 Florian Finke.
:license: MIT
"""
import os
import re
import sys
import platform
from setuptools import setup
from setuptools.command.test import test as TestCommand


def fileList(paths, relative=False, folders=False):
    """
    Generate a recursive list of files from a given path.
    """

    try:
        basestring
    except NameError:
        # Python 3
        basestring = unicode = str

    if isinstance(paths, basestring):
        paths = [paths]

    files = []

    for path in paths:
        for fileName in os.listdir(path):
            if fileName.startswith('.'):
                continue

            filePath = os.path.join(path, fileName)

            if os.path.isdir(filePath):
                if folders:
                    files.append(filePath)
                files += fileList(filePath)
            else:
                files.append(filePath)

        if relative:
            files = map(lambda x: x[len(path) + 1:], files)
    return files


package_data = {
    'cactus': map(lambda f: re.sub(r'^cactus/', '', f), fileList("cactus/skeletons"))
}

for name in os.listdir('cactus/plugins'):
    package_data["cactus"].append("plugins/{0}".format(name))

for name in os.listdir('cactus/context_processors'):
    package_data["cactus"].append("context_processors/{0}".format(name))

for name in os.listdir('cactus/tests'):
    package_data["cactus"].append("tests/{0}".format(name))

reqs = [
    'Django>=1.4.1,<1.7.0',
    'PyYAML==3.10',
    'paramiko==1.9.0',
    'slimit>=0.7.3,<=0.7.4',
    'BeautifulSoup==3.2.0',
    'boto==2.8.0',
    'hamlpy==0.82.2',
    'Twisted==13.2.0',
]
if platform.system() != "Darwin":
    reqs.append('selenium==2.27.0')


class Tox(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import tox

        errno = tox.cmdline(self.test_args)
        sys.exit(errno)

setup(
    name='Cactus',
    version="1.6.3",
    description="Static site generation and deployment.",
    long_description=__doc__,
    url='http://github.com/randomknowledge/Cactus_Refactored',
    author='Florian Finke',
    author_email='flo@randomknowledge.org',
    license='MIT',
    packages=['cactus', 'cactus.tasks', 'cactus.s3', 'cactus.templatetags', ],
    package_data=package_data,
    entry_points={
        'console_scripts': [
            'cactus = cactus.cli:main',
        ],
    },
    install_requires=reqs,
    tests_require=['tox', ],
    cmdclass={'test': Tox},
    zip_safe=False,
    classifiers=[
        #'Development Status :: 1 - Planning',
        #'Development Status :: 2 - Pre-Alpha',
        #'Development Status :: 3 - Alpha',
        #'Development Status :: 4 - Beta',
        'Development Status :: 5 - Production/Stable',
        #'Development Status :: 6 - Mature',
        #'Development Status :: 7 - Inactive',

        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',

        'Operating System :: POSIX',
        'Operating System :: MacOS',
        'Operating System :: Unix',

        'Environment :: Web Environment',
        'Framework :: Django',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',

        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)

