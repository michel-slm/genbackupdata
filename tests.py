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


"""Unit tests for genbackupdata.py"""


import os
import shutil
import unittest

import genbackupdata


class BackupDataTests(unittest.TestCase):

    dirname = "tests.dir"

    def remove_dir(self):
        if os.path.exists(self.dirname):
            shutil.rmtree(self.dirname)

    def setUp(self):
        self.remove_dir()
        self.bd = genbackupdata.BackupData(self.dirname)
        
    def tearDown(self):
        del self.bd
        self.remove_dir()

    def testDoesNotCreateDirectoryAtOnce(self):
        self.failIf(os.path.exists(self.dirname))

    def testCreatesDirectory(self):
        self.bd.create_directory()
        self.failUnless(os.path.exists(self.dirname))

    def testDoesNotFailWhenCreatingDirectoryWhenItExistsAlready(self):
        self.bd.create_directory()
        self.bd.create_directory()

    def testHasCorrectDefaultTextFileSize(self):
        self.failUnlessEqual(self.bd.get_text_file_size(), 
                             genbackupdata.DEFAULT_TEXT_FILE_SIZE)

    def testCorrectlySetsTextFileSize(self):
        self.bd.set_text_file_size(12765)
        self.failUnlessEqual(self.bd.get_text_file_size(), 12765)

    def testHasCorrectDefaultBinaryFileSize(self):
        self.failUnlessEqual(self.bd.get_binary_file_size(), 
                             genbackupdata.DEFAULT_BINARY_FILE_SIZE)

    def testCorrectlySetsBinaryFileSize(self):
        self.bd.set_binary_file_size(12765)
        self.failUnlessEqual(self.bd.get_binary_file_size(), 12765)

    def testHasCorrectTextDataPercentage(self):
        self.failUnlessEqual(self.bd.get_text_data_percentage(), 
                             genbackupdata.DEFAULT_TEXT_DATA_PERCENTAGE)

    def testCorrectlySetsTextDataPercentage(self):
        self.bd.set_text_data_percentage(42.0)
        self.failUnlessEqual(self.bd.get_text_data_percentage(), 42.0)

    def testSetsPreExistingFileCountToZeroByDefault(self):
        self.failUnlessEqual(self.bd.get_preexisting_file_count(), 0)


if __name__ == "__main__":
    unittest.main()
