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

from datetime import datetime
from errno import EEXIST, ENOENT
from os.path import dirname, isfile, join, realpath
from os import makedirs, pipe, remove, sep, walk
import subprocess
import jinja2
import yaml
from espact.exceptions import CommandErrorException, NoPackageException, PackageException, TargetException
from espact.exceptions import exception_to_package_exception
from espact.filters import default_filters

def _string_without_newline(string):
    if string != "":
        if string[-1] == "\n":
            return string[0:-1]
        else:
            return string
    else:
        return string

class _RuleCommand(str):
    pass

def _rule_command_representer(dumper, value):
    return dumper.represent_scalar(u"tag:yaml.org,2002:str", value, "|")

yaml.add_representer(_RuleCommand, _rule_command_representer)

class Target:
    def __init__(self, data, default_package_path = "package", default_target_name = "build"):
        if isinstance(data, list) and (not isinstance(data, str)) and len(data) >= 2:
            self.package_path = str(data[0])
            self.name = str(data[1])
        elif isinstance(data, list) and (not isinstance(data, str)):
            self.package_path = str(data[0])
            self.name = default_target_name
        else:
            self.package_path = default_package_path
            self.name = str(data)
     
    def __str__(self):
         return _string_without_newline(yaml.dump(self, default_flow_style = False))

    def __eq__(self, target):
        if isinstance(target, Target):
            return self.package_path == target.package_path and self.name == target.name
        else:
            return False

    def __ne__(self, target):
        return not self == target

    def __lt__(self, target):
        if isinstance(target, Target):
            if self.package_path < target.package_path:
                return True
            elif self.package_path == target.package_path and self.name < target.name:
                return True
            else:
                return False
        else:
            return True

    def __ge__(self, target):
        return not self < target

    def __gt__(self, target):
        return target < self

    def __le__(self, target):
        return not target < self

    def __cmp__(self, target):
        if self < target:
            return -1
        elif self == target:
            return 0
        else:
            return 1

    def __hash__(self):
        return hash(self.package_path) ^ hash(self.name)

def _target_representer(dumper, value):
    return dumper.represent_sequence(u"tag:yaml.org,2002:seq", [value.package_path, value.name], "[")

yaml.add_representer(Target, _target_representer)

def make_target(package_path, target_name):
    return Target([package_path, target_name], package_path)

class Rule:
    def __init__(self, data, default_package_path, default_target_name = "build"):
        if isinstance(data, dict):
            if "phony" in data:
                self.phony = (str(data["phony"]) == "true")
            else:
                self.phony = False
            if "reqs" in data:
                if isinstance(data["reqs"], list) and (not isinstance(data["reqs"], str)):
                    self.reqs = map(lambda target_data: Target(target_data, default_package_path, default_target_name), data["reqs"])
                else:
                    self.reqs = [Target(str(data["reqs"]), default_package_path, default_target_name)]
            else:
                 self.reqs = []
            if "cmd" in data:
                self.cmd = str(data["cmd"])
            else:
                self.cmd = ""
        else:
            self.phony = False
            self.reqs = []
            self.cmd = str(data)

    def __str__(self):
        return _string_without_newline(yaml.dump(self, default_flow_style = False))

def _rule_representer(dumper, value):
    pairs = [("phony", value.phony), ("reqs", value.reqs), ("cmd", _RuleCommand(value.cmd))]
    return dumper.represent_mapping(u"tag:yaml.org,2002:map", pairs)

yaml.add_representer(Rule, _rule_representer)

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
            self.rules = dict(map(lambda target_name: (target_name, Rule(rule_dict_data[target_name], path, target_name)), rule_dict_data))
        else:
            self.rules = { "build": Rule(str(rule_dict_data), path, "build") }

    def __str__(self):
        return _string_without_newline(yaml.dump(self, default_flow_style = False))

def _package_representer(dumper, value):
    pairs = [("info", value.info), ("rules", value.rules)]
    return dumper.represent_mapping(u"tag:yaml.org,2002:map", pairs)

yaml.add_representer(Package, _package_representer)

class PackageCollection:
    def __init__(self, dir = ".", work_dir = "work", vars = {}, filters = {}):
        self.dir = realpath(dir)
        self.work_dir = realpath(work_dir)
        self.vars = vars
        loader = jinja2.PrefixLoader({
                "packages": jinja2.FileSystemLoader(join(self.dir, "packages")),
                "templates": jinja2.FileSystemLoader(join(self.dir, "templates"))
            })
        self._env = jinja2.Environment(loader = loader)
        self._env.globals.update(vars)
        self._env.globals["package_collection_dir"] = self.dir
        self._env.globals["work_dir"] = self.work_dir
        self._env.globals["vars"] = vars
        self._env.filters.update(default_filters)
        self._env.filters.update(filters)
        self._package_path_cache = None
        self._package_cache = {}
        self._made_target_time_cache = {}

    def get_package(self, path):
        if path in self._package_cache:
            return self._package_cache[path]
        else:
            package = self.load_package(path)
            self._package_cache[path] = package
            return package

    def has_package(self, path):
        if self._package_path_cache != None:
            return path in self._package_path_cache
        else:
            package_tree_dir = join(self.dir, "packages")
            return isfile(join(package_tree_dir, path.replace("/", sep)) + ".info.yml")

    def load_package(self, path):
        return Package(path, self, self._env.globals.keys() + self._env.filters.keys() + ["__builtins__"])

    def clear_package_cache():
        self._package_cache = {}

    def get_package_paths(self):
        if self._package_path_cache != None:
            return self._package_path_cache
        else:
            package_paths = self.load_package_paths()
            self._package_path_cache = package_paths
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
        self._package_path_cache = None

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

    def execute_rule_command(self, target):
        package = self.get_package(target.package_path)
        try:
            makedirs(self.work_dir)
        except OSError as e:
            if e.errno != EEXIST:
                raise CommandErrorException(target, str(e))
        try:
            popen = subprocess.Popen(["sh"], stdin = subprocess.PIPE, cwd = self.work_dir)
            popen.communicate(package.rules[target.name].cmd)
            return popen.wait()
        except OSError as e:
            raise CommandErrorException(target, str(e))

    def made_target_file(self, target):
        target_tree_dir = join(self.work_dir, "targets", target.package_path.replace("/", sep)) + ".targets"
        return join(target_tree_dir, target.name.replace("/", sep)) + ".target"

    def has_made_target(self, target):
        return self.get_made_target_time(target) != None

    def add_made_target(self, target, can_create_file = True):
        current_time = datetime.now()
        self._made_target_time_cache[target] = current_time
        if can_create_file:
            target_file =  self.made_target_file(target)
            try:
                makedirs(dirname(target_file))
            except (IOError, OSError) as e:
                if e.errno != EEXIST:
                    if isinstance(e, IOError):
                        raise TargetException(target, "IO error: " + str(e))
                    else:
                        raise TargetException(target, "OS error: " + str(e))
            try:
                stream = open(target_file, "w")
                try:
                    stream.write(current_time.strftime("%Y-%m-%dT%H:%M:%S.%f") + "\n")
                finally:
                    stream.close()
            except IOError as e:
                raise TargetException(target, "IO error: " + str(e))
            except OSError as e:
                raise TargetException(target, "OS error: " + str(e))
            
    def remove_made_target(self, target):
        if target in self._made_target_time_cache:
            del self._made_target_time_cache[target]
        try:
            remove(self.made_target_file(target))
        except (IOError, OSError) as e:
            if e.errno != ENOENT:
                if isinstance(e, IOError):
                    raise TargetException(target, "IO error: " + str(e))
                else:
                    raise TargetException(target, "OS error: " + str(e))

    def get_made_target_time(self, target):
        if target in self._made_target_time_cache:
            return self._made_target_time_cache[target]
        else:
            made_target_time = self.load_made_target_time(target)
            self._made_target_time_cache[target] = made_target_time
            return made_target_time

    def load_made_target_time(self, target):
        target_file = self.made_target_file(target)
        try:
            stream = open(target_file, "r")
            try:
                line = _string_without_newline(stream.readline())
                time = datetime.strptime(line, "%Y-%m-%dT%H:%M:%S.%f")
            finally:
                stream.close()
            return time
        except (IOError, OSError) as e:
            if e.errno == ENOENT:
                return None
            else:
                if isinstance(e, IOError):
                    raise TargetException(target, "IO error: " + str(e))
                else:
                    raise TargetException(target, "OS error: " + str(e))
        except ValueError as e:
            raise TargetException(target, "incorrect date: " + str(e))

    def clear_made_target_time(self):
        self._made_target_time = {}

    def _load_yaml_template_file(self, file, *args, **kwargs):
        template = self._env.get_template(file)
        tmp_string = template.render(*args, **kwargs)
        return yaml.load(tmp_string)

    def _load_yaml_template_string(self, file, *args, **kwargs):
        template = self._jinja2_env.from_string(string)
        tmp_string = template.render(*args, **kwargs)
        return yaml.load(tmp_string)
