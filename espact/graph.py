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

class Graph:
    def dfs(self, vertex_key, preorder_fun, postorder_fun, cycle_fun, marked_vertex_keys = set([])):
        if vertex_key in marked_vertex_keys:
            return
        stack = []
        unpopped_vertex_keys = set([])
        stack.append((vertex_key, 0))
        unpopped_vertex_keys.add(vertex_key)
        marked_vertex_keys.add(vertex_key)
        preorder_fun(vertex_key)
        while stack != []:
            vertex_key, i = stack.pop()
            unpopped_vertex_keys.remove(vertex_key)
            vertex = self.vertex(vertex_key)
            while i < vertex.neighbor_count():
                if vertex.neighbor_key(i) not in marked_vertex_keys:
                    break
                elif vertex.neighbor_key(i) == vertex_key or vertex.neighbor_key(i) in unpopped_vertex_keys:
                    if not cycle_fun(vertex_key, vertex.neighbor_key(i)):
                        return
                i += 1
            if i < vertex.neighbor_count():
                stack.append((vertex_key, i + 1))
                unpopped_vertex_keys.add(vertex_key)
                stack.append((vertex.neighbor_key(i), 0))
                unpopped_vertex_keys.add(vertex.neighbor_key(i))
                marked_vertex_keys.add(vertex.neighbor_key(i))
                preorder_fun(vertex.neighbor_key(i))
            else:
                postorder_fun(vertex_key)
