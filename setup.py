# coding: utf-8
"""
Cactus

Static site generation and deployment.

:copyright: (c) 2012 Florian Finke.
:license: MIT
"""
import finddata
from setuptools import setup, os


package_data = finddata.find_package_data(
    exclude=('*.py', '*.pyc', '*$py.class', '*~', '*.bak')
)

for name in os.listdir('cactus/plugins'):
    package_data["cactus"].append("plugins/{0}".format(name))

setup(
	name='Cactus',
	version="0.0.2",
	description="Static site generation and deployment.",
	long_description=__doc__,
	url='http://github.com/randomknowledge/Cactus',
	author='Florian Finke',
	author_email='flo@randomknowledge.org',
	license='MIT',
	packages=['cactus', 'cactus.tasks', ],
    package_data=package_data,
	entry_points={
		'console_scripts': [
			'cactus = cactus.cli:main',
		],
	},
	install_requires=[
		'Django>=1.4.1,<=1.5.0',
        'PyYAML==3.10',
        'paramiko==1.9.0',
	],
	zip_safe=False,
    classifiers=[
        #'Development Status :: 1 - Planning',
        #'Development Status :: 2 - Pre-Alpha',
        'Development Status :: 3 - Alpha',
        #'Development Status :: 4 - Beta',
        #'Development Status :: 5 - Production/Stable',
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