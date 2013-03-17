# Cactus Refactored
[![Build Status](https://travis-ci.org/randomknowledge/Cactus_Refactored.png?branch=master)](https://travis-ci.org/randomknowledge/Cactus_Refactored)
___

## Table of Contents  
* [Introduction](#introduction)
* [Requirements](#requirements)
* [Installation](#installation)
* [Using `Cactus Refactored`](#using-cactus-refactored)
* [Usage example](#usage-example)
* [CSS Sprites](#css-sprites)
* [Custom Plugins](#custom-plugins)
* [Custom Context Processors](#custom-context-processors)
* [Special Template Tags](#special-template-tags)

## Introduction
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
* deploy projects via Amazon S3
* extendable via plugins (builtin and custom). Builtin plugins are:
	* Coffeescript
	* Sass/Scss
	* Less
	* CSS Sprites
	* imageopti (lossless image compression for png, gif and jpg files)
	* minify JS
	* Haml
	* Blog
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
* [Glue](https://github.com/jorgebastida/glue/)

## Installation

Install [pip](http://pypi.python.org/pypi/pip):

```console
$ sudo easy_install pip
```

Download source and install package using pip (Version 1.5 Stable):

```console
$ sudo pip install -e git+https://github.com/randomknowledge/Cactus_Refactored.git@1-5-stable#egg=Cactus
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

## CSS Sprites
To use CSS Sprites make sure the `csssprites` plugin is activated in your `config.yml` (default):
```yaml
common:
  plugins:
    # [..]
    - csssprites
    # [..]
```

You can configure the `csssprites` plugin in your `config.yml` like this (this is also the default config):
```yaml
plugins:
  csssprites:
    # path (relative to static) where the images to generate a sprite from are stored
    input_dir: img/_sprites
    
    # Directory (relative to static) in which the resulting sprite image is stored
    output_dir: img/sprites
    
    # Directory (relative to static) in which the resulting sprite css is stored
    css_dir: css/sprites
    
    # During deploy, omit 'input_dir' if set to true
    dont_deploy_input_dir: true
    
    # See http://glue.readthedocs.org/en/latest/ratios.html#how-retina-and-ratios-work
    retina: false
    
    # Glue command to be called. Change this to your needs
    command: "glue --cachebuster --crop {retina} {input_dir} --css={css_dir} --img={output_dir}"
```

Following the default settings your directory structure (inside 'static') should be like this:

```console
img/
└── _sprites/
    └── sprite1/
        ├── some_icon.png
        └── another_icon.png
```

The resulting structure will be like this:

```console
img/
├── sprites/
|   └── sprite1.png
└── css/
    └── sprites/
        └── sprite1.css
```

You also need to make sure the generated css files are included in your templates (before main.css):
```html
<head>
    [..]
    <link rel="stylesheet" href="{{ STATIC_URL }}/css/sprites/sprite1.css">
    [..]
</head>
<body>
    [..]
    <div class="sprite-sprite1-some_icon"></div>
    [..]
</body>
```
As you can see you can see for every image in the sprite there will be a class created using this syntax:

```console
sprite-<sprite_name>-<image_name>
```

See the [Glue documentation](http://glue.readthedocs.org/en/latest/quickstart.html#and-why-those-css-class-names) for details.

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