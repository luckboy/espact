# -*- coding: UTF-8 -*-
# Copyright (c) 2015, 2018 Łukasz Szpakowski
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

from os.path import isfile
from espact.exceptions import UnmakingTargetException, CommandFailureException, NoRequiredTargetException
from espact.graph import *
from espact.package import *

class _TargetVertex:
    def __init__(self, package, name, package_path):
        self.package = package
        self.name = name
        self._package_path = package_path

    def neighbor_key(self, i):
        if self.name in self.package.rules:
            return self.package.rules[self.name].reqs[i]
        else:
            raise NoRequiredTargetException(make_target(self._package_path, self.name))

    def neighbor_count(self):
        if self.name in self.package.rules:
            return len(self.package.rules[self.name].reqs)
        else:
            raise NoRequiredTargetException(make_target(self._package_path, self.name))

class _TargetGraph(Graph):
    def __init__(self, package_collection):
        self.package_collection = package_collection

    def vertex(self, vertex_key):
        package = self.package_collection.get_package(vertex_key.package_path)
        return _TargetVertex(package, vertex_key.name, vertex_key.package_path)

class Maker:
    def __init__(self, package_collection, pre_make_fun = lambda vertex_key, is_made_target: None, post_make_fun = lambda vertex_key, is_prev_made_target: None, cycle_fun = lambda vertex_key1, vertex_key2: None, is_fake = False, can_add_made_target = True, can_create_made_target_file = True):
        self.package_collection = package_collection
        self.pre_make_fun = pre_make_fun
        self.post_make_fun = post_make_fun
        self.cycle_fun = cycle_fun
        self.is_fake = is_fake
        self.can_add_made_target = can_add_made_target
        self.can_create_made_target_file = can_create_made_target_file
        self._graph = _TargetGraph(self.package_collection)
        self._marked_vertex_keys = set([])

    def make(self, target):
        self._graph.dfs(target,
            lambda vertex_key: None,
            lambda vertex_key: self._postorder(vertex_key),
            lambda vertex_key1, vertex_key2: self._cycle(vertex_key1, vertex_key2),
            self._marked_vertex_keys)

    def clear_marked_vertex_keys(self):
        self._marked_vertex_keys = set([])

    def _postorder(self, vertex_key):
        if self.package_collection.has_unmaking_target(vertex_key):
            raise UnmakingTargetException(vertex_key)
        if not self._graph.vertex(vertex_key).package.rules[vertex_key.name].phony:
            made_target_time = self.package_collection.get_made_target_time(vertex_key)
            if made_target_time == None:
                must_make = True
            else:
                package = self.package_collection.get_package(vertex_key.package_path)
                must_make = False
                for target in package.rules[vertex_key.name].reqs:
                    required_made_target_time = self.package_collection.get_made_target_time(target)
                    if self.package_collection.get_package(target.package_path).rules[target.name].phony:
                        required_made_target_time = None
                    if required_made_target_time == None or required_made_target_time == "unmaking" or required_made_target_time > made_target_time:
                        must_make = True
                        break
        else:
            must_make = True
        if must_make:
            self.pre_make_fun(vertex_key, False)
            targets_to_unmake = self._get_targets_to_unmake(vertex_key)
            if not self.is_fake:
                for target_to_unmake in targets_to_unmake:
                    if self.package_collection.has_made_target(target_to_unmake):
                        self.package_collection.add_made_target(target_to_unmake, self.can_create_made_target_file, True)
                status = self.package_collection.execute_rule_command(vertex_key)
            else:
                status = 0
            if status == 0:
                if not self.is_fake:
                    for target_to_unmake in targets_to_unmake:
                        if self.package_collection.has_made_target(target_to_unmake):
                            self.package_collection.remove_made_target(target_to_unmake)
                if self.can_add_made_target and (not self._graph.vertex(vertex_key).package.rules[vertex_key.name].phony):
                    self.package_collection.add_made_target(vertex_key, self.can_create_made_target_file)
            else:
                raise CommandFailureException(vertex_key, status)
            self.post_make_fun(vertex_key, False)
        else:
            self.pre_make_fun(vertex_key, True)
            self.post_make_fun(vertex_key, True)

    def _cycle(self, vertex_key1, vertex_key2):
        self.cycle_fun(vertex_key1, vertex_key2)
        return False

    def _get_targets_to_unmake(self, target):
        if isinstance(self.package_collection.get_package(target.package_path).rules[target.name].unmake, list):
            return self.package_collection.get_package(target.package_path).rules[target.name].unmake
        elif self.package_collection.get_package(target.package_path).rules[target.name].unmake == True:
            return map(lambda target_name: make_target(target.package_path, target_name), self.package_collection.get_package(target.package_path).rules.keys())
        else:
            return []
