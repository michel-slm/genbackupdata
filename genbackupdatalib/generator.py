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


import random
import struct


class DataGenerator(object):

    '''Generate random binary data.'''
    
    # We generate data by using a blob of suitable size. The output
    # sequence repeats the blob, where each repetition is preceded by
    # a 64-bit counter.
    #
    # We need to be relatively prime with obnam's chunk size, which
    # defaults to 64 KiB (65536 bytes). This is so that obnam does not
    # notice a lot of duplicated data, resulting in unrealistically
    # high amounts of compression in the backup store.
    #
    # Ideally, we would not generate any repeating data, but the random
    # number generator is not fast enough for that. We need to generate
    # data about as fast as the disk can write it, and the random number
    # generator is orders of magnitude slower than that.

    _blob_size = 65521
    _blob_size = 1021
    
    def __init__(self, seed):
        self._random = random.Random(seed)
        self._blob = self._generate_blob()
        self._counter = 0
        self._buffer = ''

    def _generate_blob(self):
        return ''.join(chr(self._random.randint(0, 255))
                       for i in range(self._blob_size))
        
    def generate(self, size):
        while size > len(self._buffer):
            self._buffer += self._generate_more_data()
        data = self._buffer[:size]
        self._buffer = self._buffer[size:]
        return data

    def _generate_more_data(self):
        self._counter += 1
        return struct.pack('!Q', self._counter) + self._blob

