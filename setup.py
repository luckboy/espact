#!/usr/bin/env python
# -*- coding: UTF-8 -*-
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
    from warnings import filterwarnings
    filterwarnings("ignore", category = UserWarning, module = "distutils.dist")
setup(
    name = "espact",
    description = "Easy tool for source package collections.",
    author = "Łukasz Szpakowski",
    author_email = "luckboy@vp.pl",
    license = "MIT",
    packages = ["espact"],
    scripts = ["scripts/espact"],
    install_requires = ["Jinja2", "PyYAML"],
    package_data = { "espact": ["templates/*.sh"] })
