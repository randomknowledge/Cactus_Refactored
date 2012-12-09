# coding: utf-8
"""
Cactus

Static site generation and deployment.

:copyright: (c) 2012 Florian Finke.
:license: MIT
"""
import finddata
from setuptools import setup


setup(
	name='Cactus',
	version="0.0.1",
	description="Static site generation and deployment.",
	long_description=__doc__,
	url='http://github.com/randomknowledge/Cactus',
	author='Florian Finke',
	author_email='flo@randomknowledge.org',
	license='MIT',
	packages=['cactus', 'cactus.tasks', 'cactus.plugins', ],
    package_data=finddata.find_package_data(),
	entry_points={
		'console_scripts': [
			'cactus = cactus.cli:main',
		],
	},
	install_requires=[
		'Django>=1.4.1,<=1.5.0',
	],
	zip_safe=False,
	classifiers=[],
)