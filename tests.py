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
        """Remove a directory, if it exists"""
        if os.path.exists(self.dirname):
            shutil.rmtree(self.dirname)

    def create(self, filename, contents):
        """Create a new file with the desired contents"""
        dirname = os.path.dirname(filename)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        f = file(filename, "w")
        f.write(contents)
        f.close()

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

    def testHasCorrectDefaultTextDataPercentage(self):
        self.failUnlessEqual(self.bd.get_text_data_percentage(), 
                             genbackupdata.DEFAULT_TEXT_DATA_PERCENTAGE)

    def testCorrectlySetsTextDataPercentage(self):
        self.bd.set_text_data_percentage(42.0)
        self.failUnlessEqual(self.bd.get_text_data_percentage(), 42.0)

    def testHasCorrectDefaultMaxFilesPerDirectory(self):
        self.failUnlessEqual(self.bd.get_max_files_per_directory(), 
                             genbackupdata.DEFAULT_MAX_FILES_PER_DIRECTORY)

    def testCorrectlySetsMaxFilesPerDirectory(self):
        self.bd.set_max_files_per_directory(12765)
        self.failUnlessEqual(self.bd.get_max_files_per_directory(), 12765)

    def testSetsPreExistingFileCountToZeroByDefault(self):
        self.failUnlessEqual(self.bd.get_preexisting_file_count(), 0)

    def testCanFakePreExistingFileCount(self):
        self.bd.set_preexisting_file_count(12765)
        self.failUnlessEqual(self.bd.get_preexisting_file_count(), 12765)

    def testSetsPreExistingDataSizeToZeroByDefault(self):
        self.failUnlessEqual(self.bd.get_preexisting_data_size(), 0)

    def testCanFakePreExistingDataSize(self):
        self.bd.set_preexisting_data_size(12765)
        self.failUnlessEqual(self.bd.get_preexisting_data_size(), 12765)

    def testComputesRelativeFileCountCorrectly(self):
        self.bd.set_preexisting_file_count(12765)
        self.failUnlessEqual(self.bd.get_relative_file_count(10), 1276)

    def testComputesRelativeDataSizeCorrectly(self):
        self.bd.set_preexisting_data_size(12765)
        self.failUnlessEqual(self.bd.get_relative_data_size(10), 1276)

    def testFindsNoPreExistingFilesWhenDirectoryDoesNotExist(self):
        self.bd.find_preexisting_files()
        self.failUnlessEqual(self.bd.get_preexisting_file_count(), 0)

    def testFindsNoPreExistingDataWhenDirectoryDoesNotExist(self):
        self.bd.find_preexisting_files()
        self.failUnlessEqual(self.bd.get_preexisting_data_size(), 0)

    def testChoosesFirstFilenameCorrectly(self):
        filename = self.bd.next_filename()
        self.failUnlessEqual(filename, os.path.join(self.dirname, "file0"))

    def testChoosesFirstFilenameCorrectlyTwice(self):
        filename1 = self.bd.next_filename()
        filename2 = self.bd.next_filename()
        self.failUnlessEqual(filename1, filename2)

    def testChoosesFilenameCorrectlyWhenFirstOneExistsAlready(self):
        self.bd.create_directory()
        filename1 = self.bd.next_filename()
        self.create(filename1, "")
        filename2 = self.bd.next_filename()
        self.failIfEqual(filename1, filename2)
        self.failUnlessEqual(filename2, os.path.join(self.dirname, "file1"))

    def testChoosesRootWhenItDoesNotExist(self):
        self.failUnlessEqual(self.dirname, self.bd._choose_directory())

    def testChoosesRootWhenItIsEmpty(self):
        self.bd.create_directory()
        self.failUnlessEqual(self.dirname, self.bd._choose_directory())

    def testChoosesRootDirectoryUntilMaxFileLimitIsReached(self):
        self.bd.set_max_files_per_directory(10) # For speed
        self.bd.create_directory()
        for i in range(self.bd.get_max_files_per_directory()):
            self.failUnlessEqual(self.bd._choose_directory(), self.dirname)
            self.create(self.bd.next_filename(), "")

    def testChoosesSubdirectoryWhenMaxFileLimitIsReached(self):
        self.bd.set_max_files_per_directory(10) # For speed
        self.bd.create_directory()
        for i in range(self.bd.get_max_files_per_directory()):
            self.create(self.bd.next_filename(), "")
        self.failUnlessEqual(self.bd._choose_directory(),
                             os.path.join(self.dirname, "dir0"))

    def testChoosesFirstSubdirectoryUntilMaxFileLimitIsReached(self):
        self.bd.set_max_files_per_directory(10) # For speed
        self.bd.create_directory()
        for i in range(self.bd.get_max_files_per_directory()):
            self.create(self.bd.next_filename(), "")
        for i in range(self.bd.get_max_files_per_directory()):
            self.failUnlessEqual(self.bd._choose_directory(),
                                 os.path.join(self.dirname, "dir0"))
            self.create(self.bd.next_filename(), "")

    def testChoosesSecondSubdirectoryWhenFirstOneFillsUp(self):
        self.bd.set_max_files_per_directory(10) # For speed
        self.bd.create_directory()
        for i in range(2 * self.bd.get_max_files_per_directory()):
            self.create(self.bd.next_filename(), "")
        self.failUnlessEqual(self.bd._choose_directory(),
                             os.path.join(self.dirname, "dir1"))


if __name__ == "__main__":
    unittest.main()
