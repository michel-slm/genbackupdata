# Copyright 2010  Lars Wirzenius
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


import unittest

import genbackupdatalib


class DataGeneratorTests(unittest.TestCase):

    def setUp(self):
        self.g1 = genbackupdatalib.DataGenerator(0)
        self.g2 = genbackupdatalib.DataGenerator(0)

    def test_every_generator_returns_same_sequence(self):
        amount = 1024
        self.assertEqual(self.g1.generate(amount), self.g2.generate(amount))

    def test_returns_different_sequence_for_different_seed(self):
        amount = 1024
        g3 = genbackupdatalib.DataGenerator(1)
        self.assertNotEqual(self.g1.generate(amount), g3.generate(amount))

    def test_returns_distinct_64k_chunks(self):
        size = 64 * 1024
        chunk1 = self.g1.generate(size)
        num_chunks = 100
        for i in range(num_chunks):
            self.assertNotEqual(self.g1.generate(size), chunk1)
