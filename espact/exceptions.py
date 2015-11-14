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

import jinja2
import yaml

class EspactException(Exception):
    pass

class PackageException(EspactException):
    def __init__(self, path = None, message = None):
        self.path = path
        self.message = message

    def __str__(self):
        return self.message

class NoPackageException(EspactException):
    def __init__(self, path):
        self.path = path

    def __str__(self):
        return "no package " + self.path

def exception_to_package_exception(exception, path = None):
    if isinstance(exception, jinja2.TemplateNotFound):
        return PackageException(path, "no template " + name)
    elif isinstance(exception, jinja2.TemplateSyntaxError):
        message = "template syntax error: "
        if exception.filename != None:
            message += exception.filename + ": "
        elif exception.name != None:
            message += exception.name + ": "
        message += str(exception.lineno) + ": "
        message += exception.message
        return PackageException(path, message)
    elif isinstance(exception, jinja2.TemplateSyntaxError):
        message = "template assertion error: "
        if exception.filename != None:
            message += exception.filename + ": "
        message += str(exception.lineno) + ": "
        message += exception.message
        return PackageException(path, message)
    elif isinstance(exception, jinja2.TemplateError):
        if exception.message != None:
            return PackageException(path, "template error: " + exception.message)
        else:
            return PackageException(path, "template error")
    elif isinstance(exception, yaml.YAMLError):
        message = "YAML error: " 
        message += str(exception.line) + "." + str(exception.column) + ": "
        message += exception.message
        return PackageException(path, message)
    elif isinstance(exception, IOError):
        return PackageException(path, "IO error: " + exception.message)
    else:
        return PackageException(path, "unknown error")
