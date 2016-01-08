# Espact

Espact is a tool for source package collections. Therefore, the name of this tool is Espact
(Easy Source PAckage Collection Tool). This tool can build single packages of a source package
collection or all packages of these collection. This tool was written in Python and uses YAML
and Jinja2 templates to description of packages.

## Installation

Espact requires two following packages to installation and work:

* Jinja2
* PyYAML

You can install this tool by invoke the following command:

    python setup.py install --prefix=/usr

## Usage

Building of all packages of a source package collection is easy. If you are in a directory of a
source package collection, you can build all packages by invoke the following command:

    espact

If you are in other directory, you can pass the `-d` option with a directory of a source
package collection to build all packages from other directory. If you want to build single
packages, you can invoke the following command:

    espact [-d <directory of source package collection>] <package> ...

This tool also can display a list of packages of a source package collection. You can invoke
the following command to display all packages.

    espact [-d <directory of source package collection>] -l

More information about usage of this tool is available by running of `espact` with the `--help`
option.

## Source package collection

A directory of a source package collection contains two following directories:

* `packages` - directory of packages
* `templates` - directory of templates

The first directory contains a directory tree with files of package information. If some
packages have to have their own rules, the directory tree can contain files of package rules
with their rules. Files of package information have the `.info.yml` extension and the
`.rules.yml` extension is had files of package rules.

The second directory contains a directory tree with template files for a package information
and package rules. This directory should have the `default.rules.yml` file that has default
rules.

For example, a directory structure of a source package collection is:

    |- packages
    |  |- category1
    |  |  |- package1.info.yml
    |  |  |- package2.info.yml
    |  |  |- package2.rules.yml
    |  |  `- package3.info.yml
    |  |- package4.info.yml
    |  `- package5.info.yml
    `- templates
        |- default.rules.yml
        |- template1.info.yml
        `- template2.rules.yml

### Package information

A file of package information can contain some package information in form of YAML associative
array. For example, the content of this file can be:

    name: package
    version: 0.1.0
    url: "http://www.example.org"

Files of package information are Jinja2 template of YAML file. In other words, you can use
features of Jinja2 templates in these files. 

### Package rules

Espact executes rules in files of package rules like the make program. A rule has a target and
can have required targets to make the target and shell commands. By default, Espact begins
processing of rules from rule with the `build` target for each building package.

A file of package rules contain rules in form YAML associative array. A key of this
associative array is a target name and a value for this key is an associative array of rule.
For example, the content of this file can be:

    donwload:
      cmd: |
        mkdir -p 'download/package' && \
        wget -P 'download/package' 'http://www.example.org/package-0.1.0.tar.gz'
    
    extract:
      reqs: [donwload]
      cmd: |
        mkdir -p 'build/package' && \
        tar zxf '{{work_dir|shsqe}}/download/package/package-0.1.0.tar.gz' -C 'build/package'
            
    build:
      reqs: [[required_package1], [required_package2, build_libs], extract]
      cmd: |
        cd 'build/package/package-0.1.0' && \
        {{configure()}} && \
        {{make(["all"])}} && \
        {{make(["install", "DESTDIR=" + work_dir + "/dist"])}} && \
        {{leave_from_build_dir()}}

    clean:
      phony: true
      unmake: true
      cmd: |
        rm -fr 'build/package'

The rule associative array can have the following keys with values:

* `phony` - if value is true, rule target behaves like unmade target
* `reqs` - list of required targets
* `unmake` - if value is true or list, there unmakes all targets of rule package or targets of
  list
* `cmd` - shell commands

A target in an YAML list can be represented by a list. The first element of this list is a
package path and the second element of this list is the target name. If the list has one
element, the target name is `build`. The target can be presented by a text if the rule of this
target and a rule with this list are in same package. This text is name of this target.

Shell commands are executed in the work directory. All results of execution of rules should be
in this directory. This directory will contain the `targets` with files of made targets after
making of targets.

Also, files of package rules are Jinja2 template of YAML file. In other words, you also can use
features of Jinja2 in these files.

### Templates

Files of package information and files of package rules are Jinja2 templates which can be
rendered by the Jinja2 renderer. These templates can inherit from templates in two following
directories:

* `packages` - directory of packages
* `templates` - directory of templates

Espact provides the additional global variables which are available from Jinja2 templates
and the additional filters for these templates. These global variables are presented in the
following list:

* `path` - `posixpath` module
* `basename` - `basename` function from `posixpath` module
* `dirname` - `dirname` function from `posixpath` module
* `platform` - `platform` module
* `uname` - `uname` function from `platform` module
* `re` - `re` module
* `match` - `match` function from `re` module
* `sub` - `sub` function from `re` module
* `package` - package path
* `package_collection_dir` - directory of source package collection
* `work_dir` - work directory
* `vars` - variables which are defined by the `-D` option

These filters are presented in the following list:

* `ymlqe` - escapes text in quotes for YAML files
* `ymlsqe` - escapes text in single quotes for YAML files
* `she` - escapes text for shell scripts
* `shqe` - escapes text in quotes for shell scripts
* `shsqe` - escapes text in single quotes for shell scripts
* `cme` - escapes text for CMake scripts
* `cmqe` - escapes text in quotes for CMake scripts

A package information is available from files of package rules and template files of package
rules by the `info` variable and variables except variables which cover global variables. For
example, if the `name` key with a value is defined in the `package.info.yml` file, you have
access to this value from the `package.rules.yml` file by the `name` variable and the
`info["name"]` expression.

Also, Espact provides the functions which can be used in Jinja2 templates. These functions are
presented in the following list:

* `configure(env, **other_fun_args)` - universal package configuration
* `enter_to_build_dir(**fun_args)` - universal entering to building directory
* `leave_from_build_dir(**fun_args)` - universal leaving from building directory
* `configure_for_autoconf(args, env, **other_fun_args)` - package configuration for Autoconf
* `enter_to_build_dir_for_autoconf(**fun_args)` - entering to building directory for Autoconf
* `leave_from_build_dir_for_autoconf(**fun_args)` - leaving from building directory for
  Autoconf
* `configure_for_cmake(args, env, **other_fun_args)` - package configuration for CMake
* `enter_to_build_dir_for_cmake(**fun_args)` - entering to building directory for CMake
* `leave_from_build_dir_for_cmake(**fun_args)` - leaving from building directory for CMake
* `make(args, env, **other_fun_args)` - make program 
* `gnu_make(args, env, **other_fun_args)` - GNU make program
* `bsd_make(args, env, **other_fun_args)` - BSD make program
* `packages(package_collection_dir, category)` - package paths
* `listdir(path)` - `listdir` function from `os` module for Unix-style paths
* `walk(top, topdown = True, onerror = None, followlinks = False)` - `walk` function from `os`
  module for Unix-style paths

The `args` argument is a list of command arguments. The `env` argument is a dictionary of
environment variables. These functions also can take the following arguments:

* Arguments for all functions:
    * `indent` - indentation width (by default, indentation width is 4)
    * `indentfirst` - indents lines with first line if this argument is true (by default, first
       line isn't indented)
* Arguments for configuration functions:
    * `prefix` - installation prefix
    * `build` - build machine (only for `configure_for_autoconf`)
    * `host` - host machine
    * `target` - target machine (only for `configure_for_autoconf`)
    * `build_dir` - building directory
    * `toolchain_dir` - toolchain directory
    * `find_root_dir` - search directory (only for `configure_for_cmake`)
    * `tmp_dir` - temporary directory (only for `configure_for_cmake`)
    * `ar` - ar program
    * `arflags` - flags for ar program (only for `configure_for_autoconf`)
    * `ranlib` - ranlib program
    * `ranlibflags` - flags for ranlib program (only for `configure_for_autoconf`)
    * `yacc` - parser generator
    * `yflags` - flags for parser generator (only for `configure_for_autoconf`)
    * `lex` - lexical analyzer generator
    * `lflags` - flags for lexical analyzer generator
    * `cpp` - C preprocessor (only for `configure_for_autoconf`)
    * `cppflags` - flags for C preprocessor (only for `configure_for_autoconf`)
    * `cc` - C compiler
    * `cflags` - flags for C compiler
    * `ldflags` - flags for linking
    * `libs` - libraries (only for `configure_for_autoconf`)
    * `cxx` - C++ compiler
    * `cxxflags` - flags for C++ compiler
    * `fc` - Fortran compiler
    * `fflags` - flags for Fortran compiler
    * `build_cc` - C compiler for build machine (only for `configure_for_autoconf`)
    * `autoconf_prog` - autoconf program (only for `configure_for_autoconf`)
    * `cmake_prog` - cmake program (only for `configure_for_cmake`)
* Argument for `make` function:
    * `make_prog` - make program

## License

Espact is licensed under the MIT license. See the LICENSE file for the full licensing terms.
