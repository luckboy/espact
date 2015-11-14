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

from os.path import isfile, join, realpath
from os import sep, walk
import jinja2
import yaml
from espact.filters import default_filters
from espact.exceptions import NoPackageException, PackageException, exception_to_package_exception

class RuleCommand(str):
    pass

def rule_command_representer(dumper, value):
    return dumper.represent_scalar(u"tag:yaml.org,2002:str", value, "|")

yaml.add_representer(RuleCommand, rule_command_representer)

class Rule:
    def __init__(self, data, default_req_target = "build"):
        if isinstance(data, dict):
            if "phony" in data:
                self.phony = (str(data["phony"]) == "true")
            else:
                self.phony = False
            if "reqs" in data:
                self.reqs = []
                for req in data["reqs"]:
                    if isinstance(req, list) and len(req) >= 2:
                        reqs.append([str(req[0]), str(req[1:])])
                    elif instance(req, list):
                        reqs.append([str(req[0]), default_req_target])
                    else:
                        reqs.append([str(req), default_req_target])
            else:
                 self.reqs = []
            if "cmd" in data:
                self.cmd = str(data["cmd"])
            else:
                self.cmd = None
        else:
            self.phony = False
            self.reqs = []
            self.cmd = str(data)

    def __str__(self):
        return yaml.dump(self, default_flow_style = False)

def rule_representer(dumper, value):
    pairs = [("phony", value.phony), ("reqs", value.reqs), ("cmd", RuleCommand(value.cmd))]
    return dumper.represent_mapping(u"tag:yaml.org,2002:map", pairs)

yaml.add_representer(Rule, rule_representer)

class Package:
    def __init__(self, path, collection, required_var_names):
        info_data = collection.load_package_info_data(path)
        if isinstance(info_data, dict):
            self.info = info_data
        else:
            self.info = { "name": str(info_data) }
        args = {}
        args.update(self.info)
        for name in required_var_names:
            if name in args:
                del args[name]
        args["package"] = path
        args["info"] = self.info
        rule_dict_data = collection.load_package_rule_dict_data(path, **args)
        if isinstance(rule_dict_data, dict):
            self.rules = dict(map(lambda target: (target, Rule(rule_dict_data[target], target)), rule_dict_data))
        else:
            self.rules = { "build": str(rule_dict_data) }

    def __str__(self):
        return yaml.dump(self, default_flow_style = False)

def package_representer(dumper, value):
    pairs = [("info", value.info), ("rules", value.rules)]
    return dumper.represent_mapping(u"tag:yaml.org,2002:map", pairs)

yaml.add_representer(Package, package_representer)

class PackageCollection:
    def __init__(self, dir = ".", vars = {}, filters = {}):
        self.vars = vars
        self.dir = realpath(dir)
        loader = jinja2.PrefixLoader({
                "packages": jinja2.FileSystemLoader(join(self.dir, "packages")),
                "templates": jinja2.FileSystemLoader(join(self.dir, "templates"))
            })
        self._env = jinja2.Environment(loader = loader)
        self._env.globals.update(vars)
        self._env.globals["vars"] = vars
        self._env.filters.update(default_filters)
        self._env.filters.update(filters)
        self.package_path_cache = None
        self.package_cache = {}

    def get_package(self, path):
        if path in self.package_cache:
            return self.package_cache[path]
        else:
            package = self.load_package(path)
            self.package_cache[path] = package
            return package

    def has_package(self, path):
        if self.package_path_cache != None:
            return path in self.package_path_cache
        else:
            package_tree_dir = join(self.dir, "packages")
            return isfile(join(package_tree_dir, path.replace("/", sep)) + ".info.yml")

    def load_package(self, path):
        return Package(path, self, self._env.globals.keys() + self._env.filters.keys() + ["__builtins__"])

    def clear_package_cache():
        self.package_cache = {}

    def get_package_paths(self):
        if self.package_path_cache != None:
            return self.package_path_cache
        else:
            package_paths = self.load_package_paths()
            self.package_path_cache = package_paths
            return package_paths

    def load_package_paths(self):
        package_tree_dir = join(self.dir, "packages")
        package_paths = set([])
        for dir, dirs, files in  walk(package_tree_dir):
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

    def clear_package_path_cache(self):
        self.package_path_cache = None

    def load_package_info_data(self, path):
        try:
            return self._load_yaml_template_file("packages/" + path + ".info.yml")
        except jinja2.TemplateNotFound:
            raise NoPackageException(path)
        except (jinja2.TemplateError, yaml.YAMLError, IOError) as e:
            raise exception_to_package_exception(e, path)

    def load_package_rule_dict_data(self, path, *args, **kwargs):
        try:
            return self._load_yaml_template_file("packages/" + path + ".rules.yml", *args, **kwargs)
        except jinja2.TemplateNotFound:
            return self._load_yaml_template_string("{% extends \"templates/default.rules.yml\" %}", *args, **kwargs)
        except (jinja2.TemplateError, yaml.YAMLError, IOError) as e:
            raise exception_to_package_exception(e, path)

    def _load_yaml_template_file(self, file, *args, **kwargs):
        template = self._env.get_template(file)
        tmp_string = template.render(*args, **kwargs)
        return yaml.load(tmp_string)

    def _load_yaml_template_string(self, file, *args, **kwargs):
        template = self._jinja2_env.from_string(string)
        tmp_string = template.render(*args, **kwargs)
        return yaml.load(tmp_string)
