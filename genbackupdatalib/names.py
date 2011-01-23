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

    '''Generate names for new output files.
    
    If the target directory is empty, the sequence of output files is
    always the same for the same parameters.
    
    A directory structure is also generated. The shape of the tree is
    defined by two parameters: 'max' and 'depth'. 'depth' is the number
    of levels of subdirectories to create, and 'max' is the maximum
    number of files/dirs to allow per output directory. Thus, if max is
    3 and depth is 2, the output files are: 0/0/0, 0/0/1, 0/0/2,
    0/1/0, 0/1/1, etc.
    
    If depth is zero, all output files go directly to the target
    directory, and max is ignored.
    
    '''
    
    def __init__(self, dirname, depth, max):
        self.dirname = dirname
        self.depth = depth
        self.max = max
        self.counter = 0
        
    def _path_tuple(self, n):
        '''Return tuple for dir/file numbers for nth output file.
        
        The last item in the tuple gives the file number, the precding
        items the directory numbers. Thus, a tuple (1, 2, 3) would
        mean path '1/2/3', but it is given as a tuple for easier
        manipulation.
        
        '''
        
        if self.depth == 0:
            return (n,)
        else:
            items = []
            for i in range(self.depth + 1): # +1 for filenames
                items.append(n % self.max)
                n /= self.max
            items.reverse()
        return tuple(items)
        
    def _next_candidate_name(self):
        items = self._path_tuple(self.counter)
        self.counter += 1
        return os.path.join(self.dirname, *[str(i) for i in items])
        
    def new(self):
        while True:
            name = self._next_candidate_name()
            if not os.path.exists(name):
                return name
