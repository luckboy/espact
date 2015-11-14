#!/usr/bin/env python
from distutils.core import setup
setup(
    name = "espact",
    description = "Easy tool for source package collections.",
    author = "Łukasz Szpakowski",
    author_email = "luckboy@vp.pl",
    license = "MIT",
    packages = ["espact"],
    scripts = ["scripts/espact"],
    install_requires=["jinja2", "yaml"])
