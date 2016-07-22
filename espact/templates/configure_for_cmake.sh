{#-
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
-#}
{%- extends "configure_base.sh" -%}
{%- block configure -%}
    {%- if not cmake_prog -%}
    {%- set cmake_prog = "cmake" -%}
    {%- endif -%}
    {%- if not build_dir -%}
    {%- set build_dir = "build" -%}
    {%- endif -%}
    {%- if not tmp_dir -%}
    {%- set tmp_dir = "../tmp" -%}
    {%- endif -%}
    {%- if not find_root_dir and toolchain_dir -%}
    {%- set find_root_dir = toolchain_dir -%}
    {%- endif -%}
    {%- if host -%}
    (
    {%- if not find_root_dir %}
        cc_path="`which '{{cc|shsqe}} '`"
        bin_path="`dirname "$cc_path"`"
        find_root_path="`dirname "$bin_path"`"
        awk_ors='\\n'
        awk_script='{ gsub(/[\"$()@\\^]/, "\\\\&"); gsub(/\t/, "\\t"); gsub(/\r/, "\\r"); print; }'
        escaped_find_root_path="`printf '%s' "$find_root_path" | awk -v ORS="$awk_ors" "$awk_script"`"
    {%- endif %}
        mkdir -p '{{tmp_dir|shsqe}}'
    {%- set is_found = False -%}
    {%- for host_system_pattern, system_name in [
        ("linux(-[^-]*|)", "Linux"),
        ("kfreebsd[^-]*(-[^-]*|)", "kFreeBSD"),
        ("aix[^-]*", "AIX"),
        ("bsdi[^-]*", "BSDOS"),
        ("beos", "BeOS"),
        ("bgl-blrts-gnu", "BlueGeneL"),
        ("bgp-linux", "BlueGeneP"),
        ("catamount", "Catamount"),
        ("cygwin", "CYGWIN"),
        ("darwin[^-]*", "Darwin"),
        ("dragonflybsd[^-]*", "DragonFly"),
        ("freebsd[^-]*", "FreeBSD"),
        ("gnu[^-]*", "GNU"),
        ("hpux[^-]*", "HP-UX"),
        ("haiku", "Haiku"),
        ("irix[^-]*", "IRIX"),
        ("ncr-sysv[^-]*", "MP-RAS"),
        ("netbsd[^*]", "NetBSD"),
        ("osf([1-3][^-]*|4.0(|[a-e][^-]*))", "OSF1"),
        ("openbsd[^-]*", "OpenBSD"),
        ("openvms", "OpenVMS"),
        ("qnx[^-]*", "QNX"),
        ("riscos[^-]*", "RISCos"),
        ("sco[^-]*", "SCO_SV"),
        ("sni-sysv[^-]*", "SINIX"),
        ("(sunos|solaris)[^-]*", "SunOS"),
        ("osf(4.0f|[5-9][^-]*)", "Tru64"),
        ("ultrix[^-]*", "ULTRIX"),
        ("(sysv4.2uw|unixware)[1-6][^-]*", "UNIX_SV"),
        ("(sysv5[^-]*|unixware)[7-9][^-]*", "UnixWare"),
        ("mingw[^-]*", "Windows"),
        ("xenix", "Xenix"),
        ("syllable", "syllable"),
        ("", "")
    ] -%}
    {%- if not is_found -%}
    {%- if host_system_pattern != "" -%}
    {%- if match("^[^-]+(-[^-]*-|-)" + host_system_pattern + "$", host) %}
        echo 'set(CMAKE_SYSTEM_NAME "{{system_name|cmqe|shsqe}}")' > '{{tmp_dir|shsqe}}/Toolchain.cmake'
        {%- set is_found = True -%}
    {%- endif -%}
    {%- else %}
        echo -n > '{{tmp_dir|shsqe}}/Toolchain.cmake'
    {%- endif -%}
    {%- endif -%}
    {%- endfor %}
        echo 'set(CMAKE_C_COMPILER "{{cc|cmqe|shsqe}}")' >> '{{tmp_dir|shsqe}}/Toolchain.cmake'
        echo 'set(CMAKE_CXX_COMPILER "{{cxx|cmqe|shsqe}}")' >> '{{tmp_dir|shsqe}}/Toolchain.cmake'
        echo 'set(CMAKE_Fortran_COMPILER "{{fc|cmqe|shsqe}}")' >> '{{tmp_dir|shsqe}}/Toolchain.cmake'
    {%- if toolchain_dir %}
        echo 'set(CMAKE_FIND_ROOT_PATH "{{find_root_dir|cmqe|shsqe}}")' >> '{{tmp_dir|shsqe}}/Toolchain.cmake'
    {%- else %}
        echo 'set(CMAKE_FIND_ROOT_PATH "'"$escaped_find_root_path"'")' >> '{{tmp_dir|shsqe}}/Toolchain.cmake'
    {%- endif %}
        echo 'set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)' >> '{{tmp_dir|shsqe}}/Toolchain.cmake'
        echo 'set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)' >> '{{tmp_dir|shsqe}}/Toolchain.cmake'
        echo 'set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)' >> '{{tmp_dir|shsqe}}/Toolchain.cmake'
    ) && \
    {% endif -%}
    {%- if build_dir != "." -%}
    mkdir -p '{{build_dir|shsqe}}' && \
    cd '{{build_dir|shsqe}}' && \
    {% endif -%}
    {% for name in env -%}
    {{name}}='{{env[name]|shsqe}}' \
    {% endfor -%}
    '{{cmake_prog|shsqe}}'
    {%- if host -%}
    {%- if tmp_dir.startswith("/") %} \
        -DCMAKE_TOOLCHAIN_FILE='{{tmp_dir|shsqe}}/Toolchain.cmake'
    {%- else %} \
        -DCMAKE_TOOLCHAIN_FILE='../{{tmp_dir|shsqe}}/Toolchain.cmake'
    {%- endif -%}
    {%- endif -%}
    {%- if build_type %} \
        -DCMAKE_BUILD_TYPE='{{build_type|shsqe}}'
    {%- endif -%}
    {%- if prefix %} \
        -DCMAKE_INSTALL_PREFIX='{{prefix|shsqe}}'
    {%- endif -%}
    {%- if (not host) and ar %} \
        -DCMAKE_AR='{{ar|shsqe}}'
    {%- endif -%}
    {%- if (not host) and ranlib %} \
        -DCMAKE_RANLIB='{{ranlib|shsqe}}'
    {%- endif -%}
    {%- if yacc %} \
        -DBISON_EXECUTABLE='{{yacc|shsqe}}'
    {%- endif -%}
    {%- if lex %} \
        -DFLEX_EXECUTABLE='{{lex|shsqe}}'
    {%- endif -%}
    {%- if (not host) and cc %} \
        -DCMAKE_C_COMPILER='{{cc|shsqe}}'
    {%- endif -%}
    {%- if cflags %} \
        -DCMAKE_C_FLAGS='{{cflags|shsqe}}'
    {%- endif -%}
    {%- if ldflags %} \
        -DCMAKE_EXE_LINKER_FLAGS='{{ldflags|shsqe}}'
    {%- endif -%}
    {%- if (not host) and cxx %} \
        -DCMAKE_CXX_COMPILER='{{cxx|shsqe}}'
    {%- endif -%}
    {%- if cxxflags %} \
        -DCMAKRE_CXX_FLAGS='{{cxxflags|shsqe}}'
    {%- endif -%}
    {%- if (not host) and fc %} \
        -DCMAKE_Fortran_COMPILER='{{fc|shsqe}}'
    {%- endif -%}
    {%- if fflags %} \
        -DCMAKRE_Fortran_FLAGS='{{fflags|shsqe}}'
    {%- endif -%}
    {%- if pkg_config %} \
        -DPKG_CONFIG_EXECUTABLE='{{pkg_config|shsqe}}'
    {%- endif -%}
    {%- for arg in args %} \
        '{{arg|shsqe}}'
    {%- endfor -%}
    {%- if build_dir != "." %} \
        "$espact_saved_cwd"
    {%- endif -%}
{%- endblock -%}
