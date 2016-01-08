# -*- coding: UTF-8 -*-
# Copyright (c) 2015-2016 Łukasz Szpakowski
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import os
from os import sep
from os.path import isfile, join
import platform
import re
import jinja2
from espact.filters import default_filters, shsqe
from espact.variables import default_variables

default_functions = {}

def _indent(string, width, indentfirst):
    if indentfirst:
        lines = string.split("\n")
        new_lines = []
    else:
        tmp_lines = string.split("\n")
        lines = tmp_lines[1:]
        new_lines = [tmp_lines[0]]
    new_lines += map(lambda line: (" " * width) + line, lines)
    return "\n".join(new_lines)

def _render_template(file, *args, **kwargs):
    env = jinja2.Environment(loader = jinja2.PackageLoader("espact", "templates"))
    env.globals.update(default_variables)
    env.globals.update(default_functions)
    env.filters.update(default_filters)
    template = env.get_template(file)
    new_kwargs = {}
    new_kwargs.update(kwargs)
    new_kwargs["indent"] = 0
    new_kwargs2 = {}
    new_kwargs2.update(new_kwargs)
    new_kwargs2["fun_args"] = new_kwargs
    return _indent(template.render(*args, **new_kwargs2), kwargs.get("indent", 4), kwargs.get("indentfirst", False))

def _enter_to_build_dir_for_default_build_dir(default_build_dir, **fun_args):
    build_dir = fun_args.get("build_dir", default_build_dir)
    string = "espact_saved_cwd=\"`pwd`\" && \\\n"
    string += "mkdir -p '" + shsqe(build_dir) + "' && \\\n"
    string += "cd '" + shsqe(build_dir) + "'"
    return _indent(string, fun_args.get("indent", 4), fun_args.get("indentfirst", False))

def configure(env = {}, **other_fun_args):
    return _render_template("configure.sh", env = env, **other_fun_args)

default_functions["configure"] = configure

def enter_to_build_dir(**fun_args):
    return _render_template("enter_to_build_dir.sh", **fun_args)

default_functions["enter_to_build_dir"] = enter_to_build_dir

def leave_from_build_dir(**fun_args):
    return _indent("cd \"$espact_saved_cwd\"", fun_args.get("indent", 4), fun_args.get("indentfirst", False))

default_functions["leave_from_build_dir"] = leave_from_build_dir

def configure_for_autoconf(args = [], env = {}, **other_fun_args):
    return _render_template("configure_for_autoconf.sh", args = args, env = env, **other_fun_args)

default_functions["configure_for_autoconf"] = configure_for_autoconf

def enter_to_build_dir_for_autoconf(**fun_args):
    return _enter_to_build_dir_for_default_build_dir(".", **fun_args)

default_functions["enter_to_build_dir_for_autoconf"] = enter_to_build_dir_for_autoconf

def leave_from_build_dir_for_autoconf(**fun_args):
    return leave_from_build_dir(**fun_args)

default_functions["leave_from_build_dir_for_autoconf"] = leave_from_build_dir_for_autoconf

def configure_for_cmake(args = [], env = {}, **other_fun_args):
    return _render_template("configure_for_cmake.sh", args = args, env = env, **other_fun_args)

default_functions["configure_for_cmake"] = configure_for_cmake

def enter_to_build_dir_for_cmake(**fun_args):
    return _enter_to_build_dir_for_default_build_dir("build", **fun_args)

default_functions["enter_to_build_dir_for_cmake"] = enter_to_build_dir_for_cmake

def leave_from_build_dir_for_cmake(**fun_args):
    return leave_from_build_dir(**fun_args)    

default_functions["leave_from_build_dir_for_cmake"] = leave_from_build_dir_for_cmake

def make(args = [], env = {}, **other_fun_args):
    return _render_template("make.sh", args = args, env = env, **other_fun_args)

default_functions["make"] = make

def gnu_make(args = [], env = {}, **other_fun_args):
    return _render_template("gnu_make.sh", args = args, env = env, **other_fun_args)

default_functions["gnu_make"] = gnu_make
    
def bsd_make(args = [], env = {}, **other_fun_args):
    return _render_template("bsd_make.sh", args = args, env = env, **other_fun_args)

default_functions["bsd_make"] = bsd_make

def packages(package_collection_dir, category = None):
    package_tree_dir = join(package_collection_dir, "packages")
    if category != None:
        package_dir = join(package_tree_dir, category.replace("/", sep))
    else:
        package_dir = package_tree_dir
    package_paths = set([])
    for dir, dirs, files in os.walk(package_dir):
        for file in files:
            tmp_file = join(dir, file)
            if tmp_file.endswith(".info.yml"):
                if isfile(tmp_file):
                    if tmp_file.startswith(package_tree_dir):
                        tmp_path = tmp_file[len(package_tree_dir):-9]
                        if len(tmp_path) >= 1:
                            if tmp_path[0] == sep:
                                tmp_path = tmp_path[1:]
                        package_paths.add(tmp_path.replace(sep, "/"))
    return package_paths

default_functions["packages"] = packages

def listdir(path):
    return os.listdir(path.replace("/", sep))

default_functions["listdir"] = listdir

def walk(top, topdown = True, onerror = None, followlinks = False):
    if re.match("^(2\\.[6-9](\\..+|)|[3-9](\\..+|)|[1-9][0-9](\\..+|))$", platform.python_version()):
        tuples = os.walk(top.replace("/", sep), topdown, onerror, followlinks)
    else:
        tuples = os.walk(top.replace("/", sep), topdown, onerror)
    new_tuples = []
    for dir, dirs, files in tuples:
        new_tuples.append((dir.replace(sep, "/"), dirs, files))
    return new_tuples

default_functions["walk"] = walk
