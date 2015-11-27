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
{%- extends "configure_base.sh" -%}
{%- block configure -%}
{%- if not autoreconf_prog -%}
{%- set autoreconf_prog = "autoreconf" -%}
{%- endif -%}
([ -x ./configure ] || '{{autoreconf_prog|shsqe}}' -i) && \
{% if ar -%}
AR='{{ar|shsqe}}' \
{% endif -%}
{% if arflags -%}
ARFLAGS='{{arflags|shsqe}}' \
{% endif -%}
{% if ranlib -%}
RANLIB='{{ranlib|shsqe}}' \
{% endif -%}
{% if ranlibflags -%}
RANLIBFLAGS='{{ranlibflags|shsqe}}' \
{% endif -%}
{% if yacc -%}
YACC='{{yacc|shsqe}}' \
{% endif -%}
{% if yflags -%}
YFLAGS='{{yflags|shsqe}}' \
{% endif -%}
{% if lex -%}
LEX='{{lex|shsqe}}' \
{% endif -%}
{% if lflags -%}
LFLAGS='{{lflags|shsqe}}' \
{% endif -%}
{% if cpp -%}
CPP='{{cpp|shsqe}}' \
{% endif -%}
{% if cppflags -%}
CPPFLAGS='{{cppflags|shsqe}}' \
{% endif -%}
{% if cc -%}
CC='{{cc|shsqe}}' \
{% endif -%}
{% if cflags -%}
CFLAGS='{{cflags|shsqe}}' \
{% endif -%}
{% if ldflags -%}
LDFLAGS='{{ldflags|shsqe}}' \
{% endif -%}
{% if libs -%}
LIBS='{{libs|shsqe}}' \
{% endif -%}
{% if cxx -%}
CXX='{{cxx|shsqe}}' \
{% endif -%}
{% if cxxflags -%}
CXXFLAGS='{{cxxflags|shsqe}}' \
{% endif -%}
{% if fc -%}
FC='{{fc|shsqe}}' \
{% endif -%}
{% if fflags -%}
FFLAGS='{{fflags|shsqe}}' \
{% endif -%}
{% if pkg_config -%}
PKG_CONFIG='{{pkg_config|shsqe}}' \
{% endif -%}
{% if pkg_config_path -%}
PKG_CONFIG_PATH='{{pkg_config_path|shsqe}}' \
{% endif -%}
{% if pkg_config_libdir -%}
PKG_CONFIG_LIBDIR='{{pkg_config_libdir|shsqe}}' \
{% endif -%}
{% for name in env -%}
{{name}}='{{env[name]|shsqe}}' \
{% endfor -%}
./configure
{%- if prefix %} \
    --prefix='{{prefix|shsqe}}'
{%- endif -%}
{%- if build %} \
    --build='{{build|shsqe}}'
{%- elif host or target %} \
    --build="`'{{build_cc|shsqe}}' -dumpmachine`"
{%- endif -%}
{%- if host %} \
    --host='{{host|shsqe}}'
{%- elif build or target %} \
    --host="`'{{build_cc|shsqe}}' -dumpmachine`"
{%- endif -%}
{%- if target %} \
    --target='{{target|shsqe}}'
{%- endif -%}
{%- for arg in args %} \
    '{{arg|shsqe}}'
{%- endfor -%}
{%- endblock -%}
