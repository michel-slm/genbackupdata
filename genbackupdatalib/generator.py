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


import struct

import Crypto.Cipher.ARC4


class DataGenerator(object):

    '''Generate random binary data.'''
    
    _data = 'x' * 1024**2
    
    def __init__(self, seed):
        key = struct.pack('!Q', seed)
        self._arc4 = Crypto.Cipher.ARC4.new(key)
        self._buffer = ''

    def generate(self, size):
        while len(self._buffer) < size:
            self._buffer += self._generate_junk()
        return self._split_off_data(size)

    def _generate_junk(self):
        return self._arc4.encrypt(self._data)

    def _split_off_data(self, size):
        data = self._buffer[:size]
        self._buffer = self._buffer[size:]
        return data
