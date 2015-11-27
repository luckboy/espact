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

default_filters = {}

def ymlqe(value):
    new_string = ""
    for c in string:
        if c == '\a':
            new_string += "\\a"
        elif c == '\b':
            new_string += "\\b"
        elif c == '\t':
            new_string += "\\t"
        elif c == '\n':
            new_string += "\\n"
        elif c == '\v':
            new_string += "\\v"
        elif c == '\f':
            new_string += "\\f"
        elif c == '\r':
            new_string += "\\r"
        elif c == '\27':
            new_string += "\\27"
        elif c == '"':
            new_string += "\\\""
        elif c == '\\':
            new_string += "\\\\"
        elif (ord(c) >= 0x00 and ord(c) <= 0x1f) or ord(c) == 0x7f:
            new_string += "\\x{0:02X}".format(ord(c)) 
        elif (ord(c) >= 0x80 and ord(c) <= 0x84) or (ord(c) >= 0x86 and ord(c) <= 0x9f) or \
            (ord(c) >= 0xd800 and ord(c) <= 0xdfff) or (ord(c) >= 0xfffe and ord(c) <= 0xffff):
            new_string += "\\u{0:04X}".format(ord(c))
        elif ord(c) >= 0x110000:
            new_string += "\\U{0:08X}".format(ord(c))
        else:
            new_string += c
    return new_string

default_filters["ymlqe"] = ymlqe

def ymlsqe(string):
    new_string = ""
    for c in string:
        if c == "'":
            new_string += "''"
        else:
            new_string += c
    return new_string

default_filters["ymlsqe"] = ymlsqe

def she(string):
    new_string = ""
    for c in string:
        if c in "\t \"#$%&\'()*;<=>?[\\`|~":
            new_string += "\\" + c
        elif c == "\n":
            new_string += " "
        else:
            new_string += c
    return new_string

default_filters["she"] = she

def shqe(string):
    new_string = ""
    for c in string:
        if c in "\"$\\`":
            new_string += "\\" + c
        else:
            new_string += c
    return new_string

default_filters["shqe"] = shqe

def shsqe(string):
    new_string = ""
    for c in string:
        if c == "'":
            new_string += "'\\''"
        else:
            new_string += c
    return new_string

default_filters["shsqe"] = shsqe

def cme(string):
    new_string = ""
    for c in string:
        if c == "\t":
            new_string += "\\t"
        elif c == "\n":
            new_string += "\\n"
        elif c == "\r":
            new_string += "\\r"
        elif c in " \"#$();@\\^":
            new_string += "\\" + c
        else:
            new_string += c
    return new_string

default_filters["cme"] = cme

def cmqe(string):
    new_string = ""
    for c in string:
        if c == "\t":
            new_string += "\\t"
        elif c == "\n":
            new_string += "\\n"
        elif c == "\r":
            new_string += "\\r"
        elif c in "\"$()@\\^":
            new_string += "\\" + c
        else:
            new_string += c
    return new_string

default_filters["cmqe"] = cmqe
