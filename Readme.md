# Cactus Refactored
[![Build Status](https://travis-ci.org/randomknowledge/Cactus_Refactored.png?branch=master)](https://travis-ci.org/randomknowledge/Cactus_Refactored)
___
`Cactus Refactored` is a static website generator using [Python](http://www.python.org/)
and the [Django template system](https://docs.djangoproject.com/en/dev/topics/templates/).
Originally I wrote this as a refactored version of [Cactus](https://github.com/koenbok/Cactus),
so credits go to [Koenbok](https://github.com/koenbok/).
By now `Cactus Refactored` has the following features:

* create projects from skeletons (builtin or custom)
	* builtin skeletons are `default` and `blog`
* serve project via builtin development webserver with auto-reload-functionality working on Windows, Mac OS X and Linux
* (obviously) build projects
* deploy projects via SSH (public key auth and simple password auth are supported)
* extendable via plugins (builtin and custom). Builtin plugins are:
	* Coffeescript
	* Sass
	* imageopti (lossless image compression for png, gif and jpg files)
	* minify JS
	* Blog
* completely configurable via [YAML](http://de.wikipedia.org/wiki/YAML). See [config.yml](https://github.com/randomknowledge/Cactus_Refactored/blob/master/cactus/skeletons/default/config.yml) for details.

____

## Requirements
* [Django](https://www.djangoproject.com/)
* [PyYAML](http://pyyaml.org/)
* [paramiko](http://www.lag.net/paramiko/)
* [slimit](http://slimit.readthedocs.org/en/latest/)
* [selenium](http://pypi.python.org/pypi/selenium)
* [BeautifulSoup](http://www.crummy.com/software/BeautifulSoup/)

## Installation

Install [pip](http://pypi.python.org/pypi/pip):

```console
$ sudo easy_install pip
```

Download source and install package using pip (Version 1.0.0):

```console
$ sudo pip install -e git+https://github.com/randomknowledge/Cactus_Refactored.git@v1.0.0#egg=Cactus
```

Download source and install package using pip (Development version):

```console
$ sudo pip install -e git+https://github.com/randomknowledge/Cactus_Refactored.git#egg=Cactus
```


## Using `Cactus Refactored`

```console
Usage: cactus [serve|create|help|build|deploy]

    serve [listen_address:port]: Serve you website at local development server
    create <path> [<skeleton type>|<skeleton path>]: Create a new website skeleton at the given path.
    help <task>: Get help for specified task.
    build: Rebuild your site from source files
    deploy [target] [--build=yes|no]: deploy project to the given target.
```

## Usage example

```console
$ cactus create www.mywebsite.com
$ cd www.mywebsite.com
$ cactus serve
<CTRL>+C
$ cactus build
```
