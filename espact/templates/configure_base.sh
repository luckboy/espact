{#-
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
-#}
{%- if host or toolchain_dir -%}
{%- set toolchain_prefix = "" -%}
{%- if toolchain_dir -%}
{%- set toolchain_prefix = toolchain_prefix + toolchain_dir + "/bin/" -%}
{%- endif -%}
{%- if host -%}
{%- set toolchain_prefix = toolchain_prefix + host + "-" -%}
{%- endif -%}
{%- if not ar -%}
{%- set ar = toolchain_prefix + "ar" -%}
{%- endif -%}
{%- if not ranlib -%}
{%- set ranlib = toolchain_prefix + "ranlib" -%}
{%- endif -%}
{%- if not cpp -%}
{%- set cpp = toolchain_prefix + "cpp" -%}
{%- endif -%}
{%- if not cc -%}
{%- set cc = toolchain_prefix + "gcc" -%}
{%- endif -%}
{%- if not cxx -%}
{%- set cxx = toolchain_prefix + "g++" -%}
{%- endif -%}
{%- if not fc -%}
{%- set fc = toolchain_prefix + "gfortran" -%}
{%- endif -%}
{%- endif -%}
{%- if toolchain_dir %}
{%- if not yacc -%}
{%- set yacc = toolchain_dir + "/bin/bison" -%}
{%- endif -%}
{%- if not lex -%}
{%- set lex = toolchain_dir + "/bin/flex" -%}
{%- endif -%}
{%- endif -%}
{%- if not build_cc -%}
{%- set build_cc = "gcc" -%}
{%- endif -%}
espact_saved_cwd="`pwd`" && \
{% block configure -%}{%- endblock -%}
