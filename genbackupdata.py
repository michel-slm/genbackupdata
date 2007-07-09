#!/usr/bin/python
#
# Copyright (C) 2007  Lars Wirzenius <liw@iki.fi>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.


"""Generate backup test data"""


import os


KiB = 2 ** 10   # A kibibyte
MiB = 2 ** 20   # A mebibyte

# Defaults for various settings in the BackupData class.
DEFAULT_TEXT_FILE_SIZE = 10 * KiB
DEFAULT_BINARY_FILE_SIZE = 10 * MiB
DEFAULT_TEXT_DATA_PERCENTAGE = 10.0


class BackupData:

    """This class represents the directory with backup data"""
    
    def __init__(self, dirname):
        self._dirname = dirname
        self._text_file_size = DEFAULT_TEXT_FILE_SIZE
        self._binary_file_size = DEFAULT_BINARY_FILE_SIZE
        self._text_data_percentage = DEFAULT_TEXT_DATA_PERCENTAGE
        self._preexisting_file_count = 0
        self._preexisting_data_size = 0
        
    def create_directory(self):
        """Create the backup data directory, if it doesn't exist already"""
        if not os.path.exists(self._dirname):
            os.mkdir(self._dirname)

    def get_text_file_size(self):
        """Return size of newly created text files"""
        return self._text_file_size

    def set_text_file_size(self, size):
        """Set size of newly created text files"""
        self._text_file_size = size

    def get_binary_file_size(self):
        """Return size of newly created binary files"""
        return self._binary_file_size

    def set_binary_file_size(self, size):
        """Set size of newly created binary files"""
        self._binary_file_size = size

    def get_text_data_percentage(self):
        """Return percentage of text data of new data that gets created"""
        return self._text_data_percentage

    def set_text_data_percentage(self, percent):
        """Set percentage of text data of new data that gets created"""
        self._text_data_percentage = percent

    def get_preexisting_file_count(self):
        """Return count of files that existed in directory in the beginning"""
        return self._preexisting_file_count

    def set_preexisting_file_count(self, count):
        """Set count of files that existed in directory in the beginning
        
        This is useful only for unit tests.
        
        """
        self._preexisting_file_count = count

    def get_preexisting_data_size(self):
        """Return size of data that existed in directory in the beginning"""
        return self._preexisting_data_size

    def set_preexisting_data_size(self, size):
        """Set size of data that existed in directory in the beginning
        
        This is useful only for unit tests.
        
        """
        self._preexisting_data_size = size

    def get_relative_file_count(self, percent):
        """Return PERCENT percent of pre-existing file count"""
        return int(0.01 * percent * self.get_preexisting_file_count())

    def get_relative_data_size(self, percent):
        """Return PERCENT percent of pre-existing data"""
        return int(0.01 * percent * self.get_preexisting_data_size())

    def find_preexisting_files(self):
        """Find all the files that exists in the directory right now"""
