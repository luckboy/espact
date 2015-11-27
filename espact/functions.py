# -*- coding: UTF-8 -*-
# Copyright (c) 2015 Łukasz Szpakowski
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

import platform
import re
import jinja2
from espact.filters import default_filters

default_functions = {}

def _render_template(file, *args, **kwargs):
    env = jinja2.Environment(loader = jinja2.PackageLoader("espact", "templates"))
    env.globals.update(default_functions)
    env.globals["platform"] = platform
    env.globals["re"] = re
    env.globals["match"] = re.match
    env.globals["sub"] = re.sub
    env.filters.update(default_filters)
    template = env.get_template(file)
    new_kwargs = {}
    new_kwargs.update(kwargs)
    new_kwargs["fun_args"] = kwargs
    if "indent" in kwargs:
        indent = kwargs["indent"]
    else:
        indent = 4
    string = template.render(*args, **new_kwargs)
    if ("indentfirst" in kwargs and kwargs["indentfirst"] == True):
        lines = string.split("\n")
        new_lines = []
    else:
        tmp_lines = string.split("\n")
        lines = tmp_lines[1:-1]
        new_lines = [tmp_lines[0]]
    new_lines += map(lambda line: (" " * indent) + line, lines)
    return "\n".join(new_lines)

def configure(env = {}, **fun_args):
    return _render_template("configure.sh", env = env, **fun_args)

default_functions["configure"] = configure

def end_configure():
    return _render_template("end_configure.sh")

default_functions["end_configure"] = end_configure

def configure_for_autoconf(args = [], env = {}, **other_fun_args):
    return _render_template("configure_for_autoconf.sh", args = args, env = env, **other_fun_args)

default_functions["configure_for_autoconf"] = configure_for_autoconf

def end_configure_for_autoconf():
    return "true"

default_functions["end_configure_for_autoconf"] = end_configure_for_autoconf

def configure_for_cmake(args = [], env = {}, **other_fun_args):
    return _render_template("configure_for_cmake.sh", args = args, env = env, **other_fun_args)

default_functions["configure_for_cmake"] = configure_for_cmake

def end_configure_for_cmake():
    return "cd \"$espact_saved_cwd\""

default_functions["end_configure_for_cmake"] = end_configure_for_cmake

def make(args = [], env = {}):
    return _render_template("make.sh", args = args, env = env)

default_functions["make"] = make

def gnu_make(args = [], env = {}):
    return _render_template("gnu_make.sh", args = args, env = env)

default_functions["gnu_make"] = gnu_make
    
def bsd_make(args = [], env = []):
    return _render_template("bsd_make.sh", args = args, env = env)

default_functions["bsd_make"] = bsd_make
