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


class NameGenerator(object):

    '''Generate names for new output files.'''
    
    def __init__(self, dirname):
        self.dirname = dirname
        self.counter = 0
        
    def _next_candidate_name(self):
        self.counter += 1
        return os.path.join(self.dirname, 'file%d' % self.counter)
        
    def new(self):
        while True:
            name = self._next_candidate_name()
            if not os.path.exists(name):
                return name
