# Copyright 2011  Lars Wirzenius
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import os
import shutil
import tempfile
import unittest

import genbackupdatalib


class NameGeneratorTests(unittest.TestCase):

    def setUp(self):
        self.tempdir = tempfile.mkdtemp()
        self.depth = 2
        self.max = 3
        self.names = self.new()
        
    def tearDown(self):
        shutil.rmtree(self.tempdir)
        
    def new(self):
        return genbackupdatalib.NameGenerator(self.tempdir, self.depth,
                                              self.max)

    def test_generates_name_that_is_inside_target_directory(self):
        name = self.names.new()
        self.assert_(name.startswith(self.tempdir + os.sep))

    def test_generates_different_names_every_time(self):
        names = set(self.names.new() for i in range(10))
        self.assertEqual(len(names), 10)

    def test_generates_names_that_do_not_exist(self):
        for i in range(10):
            name = self.names.new()
            self.assertFalse(os.path.exists(name))

    def test_generates_the_same_sequence_with_every_instance(self):
        n = 10
        first = [self.names.new() for i in range(n)]
        names2 = self.new()
        second = [names2.new() for i in range(n)]
        self.assertEqual(first, second)

    def test_does_not_generate_names_of_existing_files(self):
        name = self.names.new()
        os.makedirs(os.path.dirname(name))
        file(name, 'w').close()
        names2 = self.new()
        name2 = names2.new()
        self.assertNotEqual(name, name2)
        self.assertFalse(os.path.exists(name2))

    def test_converts_file_sequence_number_into_right_path_tuple(self):
        self.assertEqual(self.names._path_tuple(0), (0, 0, 0))
        self.assertEqual(self.names._path_tuple(1), (0, 0, 1))
        self.assertEqual(self.names._path_tuple(2), (0, 0, 2))
        self.assertEqual(self.names._path_tuple(3), (0, 1, 0))
        self.assertEqual(self.names._path_tuple(4), (0, 1, 1))
        self.assertEqual(self.names._path_tuple(5), (0, 1, 2))
        self.assertEqual(self.names._path_tuple(6), (0, 2, 0))
        self.assertEqual(self.names._path_tuple(9), (1, 0, 0))
        self.assertEqual(self.names._path_tuple(18), (2, 0, 0))
        self.assertEqual(self.names._path_tuple(27), (3, 0, 0))

    def test_returns_1tuple_for_depth_zero(self):
        names = genbackupdatalib.NameGenerator(self.tempdir, 0, 1)
        self.assertEqual(names._path_tuple(42), (42,))

