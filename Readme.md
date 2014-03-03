# Cactus Refactored
[![Build Status](https://travis-ci.org/randomknowledge/Cactus_Refactored.png?branch=master)](https://travis-ci.org/randomknowledge/Cactus_Refactored)
___

## Table of Contents  
* [Introduction](#introduction)
* [Requirements](#requirements)
* [Installation](#installation)
* [Using `Cactus Refactored`](#using-cactus-refactored)
* [Usage example](#usage-example)
* [Custom Plugins](#custom-plugins)
* [Custom Context Processors](#custom-context-processors)
* [Special Template Tags](#special-template-tags)
* [Known Bugs/Errors](#known-bugserrors)

## Introduction
`Cactus Refactored` is a static website generator using [Python](http://www.python.org/)
and the [Django template system](https://docs.djangoproject.com/en/dev/topics/templates/).
Originally I wrote this as a refactored version of [Cactus](https://github.com/koenbok/Cactus),
so credits go to [Koenbok](https://github.com/koenbok/).
By now `Cactus Refactored` has the following features:

* create projects from skeletons (builtin or custom)
	* builtin skeleton is `default`
* serve project via builtin development webserver with auto-reload-functionality working on Windows, Mac OS X and Linux
* (obviously) build projects
* deploy projects via SSH (public key auth and simple password auth are supported)
* deploy projects via Amazon S3
* extendable via plugins (builtin and custom). Builtin plugins are:
	* Coffeescript
	* Sass/Scss
	* Less
	* imageopti (lossless image compression for png, gif and jpg files)
	* minify JS
	* Haml
* custom template context processors (see [context_processors/default.py](https://github.com/randomknowledge/Cactus_Refactored/blob/master/cactus/context_processors/default.py) for an example)
* completely configurable via [YAML](http://de.wikipedia.org/wiki/YAML). See [config.yml](https://github.com/randomknowledge/Cactus_Refactored/blob/master/cactus/skeletons/default/config.yml) for details.

____

## Requirements
* [Django](https://www.djangoproject.com/)
* [PyYAML](http://pyyaml.org/)
* [paramiko](http://www.lag.net/paramiko/)
* [slimit](http://slimit.readthedocs.org/en/latest/)
* [selenium](http://pypi.python.org/pypi/selenium)
* [BeautifulSoup](http://www.crummy.com/software/BeautifulSoup/)
* [boto](https://github.com/boto/boto/)
* [HamlPy](https://github.com/jessemiller/HamlPy/)
* [Twisted](https://twistedmatrix.com)

## Installation

Install [pip](http://pypi.python.org/pypi/pip):

```console
$ sudo easy_install pip
```

Download source and install package using pip (Version 1.6 Stable):

```console
$ sudo pip install -e git+https://github.com/randomknowledge/Cactus_Refactored.git@1-6-stable#egg=Cactus
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

## Custom Plugins

To activate custom plugins inside your project, add them to a directory named `plugins` inside your project directory. The plugin filename must be unique and the file must contain a class that extends [CactusPluginBase](https://github.com/randomknowledge/Cactus_Refactored/blob/master/cactus/plugin_base.py). Have a look at the [minifyjs plugin](https://github.com/randomknowledge/Cactus_Refactored/blob/master/cactus/plugins/minifyjs.py) for a simple example.


## Custom Context Processors

With Context Processors you can add custom variables to the template context. Those variables can then be accessed from inside your templates.

To activate custom template processors inside your project, add them to a directory named `context_processors` inside your project directory. The context-processor's filename must be unique and the file must contain a class that extends [ContextProcessorBase](https://github.com/randomknowledge/Cactus_Refactored/blob/master/cactus/context_processor_base.py). Have a look at the [default context processor](https://github.com/randomknowledge/Cactus_Refactored/blob/master/cactus/context_processors/default.py) for a simple example.

Plugins also have their own template context (wich is empty by default). Just override `templateContext` inside a plugin and make sure it returns a dictionary. Plugin contexts are automatically namespaces to `plugins.<plugin_name>`.

__Plugin context example__

```python
# file: plugins/mycustomplugin.py
class MyCustomPlugin(CactusPluginBase):
	def templateContext(self, *args, **kwargs):
		return {
			"name": "World"
		}
```

```html
<html>
<body>
Hello {{ plugins.mycustomplugin.name }}!
</body>
</html>
```


__custom template context example__

```python
# file: context_processors/customcontext.py
class MyCustomContext(ContextProcessorBase):
	def context(self):
		return {
			"name": "World"
		}
```

```html
<html>
<body>
Hello {{ name }}!
</body>
</html>
```

## Special Template Tags
Right now `Cactus Refactored` has one custom template tag: `render_block_from_file`.
Use it like this:
```html
{% render_block_from_file 'another-page' 'blockname' %}
```
This will render the block 'blockname' from the page 'another-page' inside your template.
To render a block from a page in a subfolder use the followinf syntax:
```html
{% render_block_from_file 'sub/folder/another-page' 'blockname' %}
```

## Known Bugs/Errors
### Error Loading osascript
There is an error loading the Adobe Unit Types osascript under OSX 1.6.6+. It is used to refresh a page in the browser.
Solution: Install the update from Adobe under /Library/ScriptingAdditions available here: http://helpx.adobe.com/photoshop/kb/unit-type-conversion-error-applescript.html

Thanks to [@remeiberlin](https://github.com/remeiberlin) for [reporting](https://github.com/randomknowledge/Cactus_Refactored/issues/3) this!
