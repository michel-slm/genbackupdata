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
import zlib

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

    def read_file(self, filename):
        """Return the entire contents of a file"""
        f = file(filename)
        data = f.read()
        f.close()
        return data

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

    def testHasCorrectDefaultSeed(self):
        self.failUnlessEqual(self.bd.get_seed(), genbackupdata.DEFAULT_SEED)

    def testCorrectlySetsSeed(self):
        self.bd.set_seed(12765)
        self.failUnlessEqual(self.bd.get_seed(), 12765)

    def testHasNoPRNGInitially(self):
        self.failUnlessEqual(self.bd.get_prng(), None)

    def testCreatesPRNGWhenRequested(self):
        self.bd.init_prng()
        self.failIfEqual(self.bd.get_prng(), None)

    def testFailsIfSeedGetsSetAfterPRNGHasBeenCreatedTwice(self):
        self.bd.init_prng()
        self.failUnlessRaises(AssertionError, self.bd.set_seed, 12765)

    def testHasCorrectDefaultBinaryChunkSize(self):
        self.failUnlessEqual(self.bd.get_binary_chunk_size(), 
                             genbackupdata.DEFAULT_BINARY_CHUNK_SIZE)

    def testCorrectlySetsBinaryChunkSize(self):
        self.bd.set_binary_chunk_size(12765)
        self.failUnlessEqual(self.bd.get_binary_chunk_size(), 12765)

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

    def testFindsPreExistingFilesAndDAtaCorrectly(self):
        file_count = 10
        file_size = self.bd.get_text_file_size()
        data = self.bd.generate_text_data(file_size)
        for i in range(file_count):
            self.create(self.bd.next_filename(), data)
        self.bd.find_preexisting_files()
        self.failUnlessEqual(self.bd.get_preexisting_file_count(), file_count)
        self.failUnlessEqual(self.bd.get_preexisting_data_size(), 
                             file_count * file_size)

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

    def testGeneratesSmallAmountOfTextDataCorrectly(self):
        n = 128
        self.failUnlessEqual(self.bd.generate_text_data(n),
                             genbackupdata.LOREM_IPSUM[:n])

    def testGeneratesLargeAmountOfTextDataCorrectly(self):
        n = len(genbackupdata.LOREM_IPSUM)
        self.failUnlessEqual(self.bd.generate_text_data(n * 2),
                             genbackupdata.LOREM_IPSUM * 2)

    def testGeneratesRequestedAmountOfBinaryData(self):
        n = 128
        self.failUnlessEqual(len(self.bd.generate_binary_data(n)), n)

    def testGeneratesBinaryDataWhichDoesNotCompressWell(self):
        n = 10 * 1024
        data = zlib.compress(self.bd.generate_binary_data(n))
        self.failUnless(len(data) > 0.95* n)

    def testCreatesSubdirectoriesCorrectly(self):
        filename = os.path.join(self.dirname, "subdir", "filename")
        self.bd.create_subdirectories(filename)
        self.failUnless(os.path.isdir(os.path.dirname(filename)))

    def testCreatesTextFileCorrectly(self):
        size = self.bd.get_text_file_size()
        filename = self.bd.next_filename()
        self.bd.create_text_file(size)
        self.failUnless(os.path.isfile(filename))
        self.failUnlessEqual(self.read_file(filename), 
                             self.bd.generate_text_data(size))

    def testCreatesBinaryFileCorrectly(self):
        size = self.bd.get_binary_chunk_size() + 1
        filename = self.bd.next_filename()
        self.bd.create_binary_file(size)
        self.failUnless(os.path.isfile(filename))
        self.failUnlessEqual(os.path.getsize(filename), size)

    def failUnlessTextFile(self, filename):
        data = self.read_file(filename)
        self.failUnlessEqual(data, self.bd.generate_text_data(len(data)))

    def testCreatesTextFilesOnlyCorrectly(self):
        self.bd.set_text_data_percentage(100)
        count = 10
        size = count * self.bd.get_text_file_size()
        self.bd.create_files(size)
        self.bd.find_preexisting_files()
        self.failUnlessEqual(self.bd.get_preexisting_file_count(), count)
        self.failUnlessEqual(self.bd.get_preexisting_data_size(), size)
        for root, dirs, filenames in os.walk(self.dirname):
            for filename in filenames:
                pathname = os.path.join(root, filename)
                self.failUnlessTextFile(pathname)

    def failIfTextFile(self, filename):
        data = self.read_file(filename)
        self.failIfEqual(data, self.bd.generate_text_data(len(data)))

    def testCreatesNoTextFilesCorrectly(self):
        self.bd.set_text_data_percentage(0)
        count = 1
        size = count * self.bd.get_text_file_size()
        self.bd.create_files(size)
        self.bd.find_preexisting_files()
        self.failUnlessEqual(self.bd.get_preexisting_file_count(), 1)
        self.failUnlessEqual(self.bd.get_preexisting_data_size(), size)
        for root, dirs, filenames in os.walk(self.dirname):
            for filename in filenames:
                pathname = os.path.join(root, filename)
                self.failIfTextFile(pathname)

    def testDeletesFilesCorrectly(self):
        size = 100
        self.bd.set_text_file_size(1)
        self.bd.set_binary_file_size(1)
        self.bd.create_files(size)
        self.bd.find_preexisting_files()
        count = self.bd.get_preexisting_file_count()
        to_delete = count/3
        remaining = count - to_delete
        self.bd.delete_files(to_delete)
        self.bd.find_preexisting_files()
        self.failUnlessEqual(self.bd.get_preexisting_file_count(), remaining)

    def testRenameFiles(self):
        self.bd.create_directory()
        filename = self.bd.next_filename()
        self.create(filename, "")
        new_filename = self.bd.next_filename()
        self.bd.rename_files(1)
        self.failIf(os.path.exists(filename))
        self.failUnless(os.path.exists(new_filename))

    def testHasCorrectDefaultModifyPercentage(self):
        self.failUnlessEqual(self.bd.get_modify_percentage(),
                             genbackupdata.DEFAULT_MODIFY_PERCENTAGE)

    def testCorrectlySetsModifyPercentage(self):
        self.bd.set_modify_percentage(42.0)
        self.failUnlessEqual(self.bd.get_modify_percentage(), 42.0)

    def testModifyFiles(self):
        size = 100
        self.bd.create_directory()
        filename = self.bd.next_filename()
        orig_data = "x" * size
        self.create(filename, orig_data)
        self.bd.modify_files(size)
        self.failUnlessEqual(len(self.read_file(filename)), 2 * size)


class CommandLineParserTests(unittest.TestCase):

    dirname = "tests.dir"

    def setUp(self):
        self.bd = genbackupdata.BackupData(self.dirname)
        self.clp = genbackupdata.CommandLineParser(self.bd)
        
    def tearDown(self):
        del self.bd
        del self.clp

    def testDoesNotTouchDefaultsWithEmptyCommandLine(self):
        self.failUnlessEqual(self.bd.get_seed(), genbackupdata.DEFAULT_SEED)
        self.failUnlessEqual(self.bd.get_binary_chunk_size(),
                             genbackupdata.DEFAULT_BINARY_CHUNK_SIZE)
        self.failUnlessEqual(self.bd.get_text_file_size(),
                             genbackupdata.DEFAULT_TEXT_FILE_SIZE)
        self.failUnlessEqual(self.bd.get_binary_file_size(),
                             genbackupdata.DEFAULT_BINARY_FILE_SIZE)
        self.failUnlessEqual(self.bd.get_text_data_percentage(),
                             genbackupdata.DEFAULT_TEXT_DATA_PERCENTAGE)
        self.failUnlessEqual(self.bd.get_max_files_per_directory(),
                             genbackupdata.DEFAULT_MAX_FILES_PER_DIRECTORY)
        self.failUnlessEqual(self.bd.get_modify_percentage(),
                             genbackupdata.DEFAULT_MODIFY_PERCENTAGE)

    def testParsesPlainSizeCorrectly(self):
        self.failUnlessEqual(self.clp.parse_size("12765"), 12765)

    def testParsesAbsoluteSizeSuffixesCorrectly(self):
        self.failUnlessEqual(self.clp.parse_size("3k"), 3 * genbackupdata.KiB)
        self.failUnlessEqual(self.clp.parse_size("3K"), 3 * genbackupdata.KiB)
        self.failUnlessEqual(self.clp.parse_size("3m"), 3 * genbackupdata.MiB)
        self.failUnlessEqual(self.clp.parse_size("3M"), 3 * genbackupdata.MiB)
        self.failUnlessEqual(self.clp.parse_size("3g"), 3 * genbackupdata.GiB)
        self.failUnlessEqual(self.clp.parse_size("3G"), 3 * genbackupdata.GiB)
        self.failUnlessEqual(self.clp.parse_size("3t"), 3 * genbackupdata.TiB)
        self.failUnlessEqual(self.clp.parse_size("3T"), 3 * genbackupdata.TiB)

    def testParsesRelativeSizeSuffixCorrectly(self):
        self.failUnlessEqual(self.clp.parse_size("10%", 12765), 1276)

    def testParsesRelativeSizeSuffixCorrectlyWithMissingBaseSize(self):
        self.failUnlessEqual(self.clp.parse_size("10%"), 0)

    def testParsesPlainCountCorrectly(self):
        self.failUnlessEqual(self.clp.parse_count("12765"), 12765)

    def testParsesAbsoluteCountSuffixesCorrectly(self):
        self.failUnlessEqual(self.clp.parse_count("3k"), 3 * 10**3)
        self.failUnlessEqual(self.clp.parse_count("3K"), 3 * 10**3)
        self.failUnlessEqual(self.clp.parse_count("3m"), 3 * 10**6)
        self.failUnlessEqual(self.clp.parse_count("3M"), 3 * 10**6)
        self.failUnlessEqual(self.clp.parse_count("3g"), 3 * 10**9)
        self.failUnlessEqual(self.clp.parse_count("3G"), 3 * 10**9)
        self.failUnlessEqual(self.clp.parse_count("3t"), 3 * 10**12)
        self.failUnlessEqual(self.clp.parse_count("3T"), 3 * 10**12)

    def testParsesRelativeCountSuffixCorrectly(self):
        self.failUnlessEqual(self.clp.parse_count("10%", 12765), 1276)

    def testParsesRelativeCountSuffixCorrectlyWithMissingBaseSize(self):
        self.failUnlessEqual(self.clp.parse_count("10%"), 0)

    def testHandlesOptionForSeed(self):
        optons, args = self.clp.parse(["--seed=12765"])
        self.failUnlessEqual(args, [])
        self.failUnlessEqual(self.bd.get_seed(), 12765)

    def testHandlesOptionForMaxCount(self):
        options, args = self.clp.parse(["--max-count=12765"])
        self.failUnlessEqual(args, [])
        self.failUnlessEqual(self.bd.get_max_files_per_directory(), 12765)

    def testHandlesOptionForPercentageTextData(self):
        options, args = self.clp.parse(["--percentage-text-data=4.2"])
        self.failUnlessEqual(args, [])
        self.failUnlessEqual(self.bd.get_text_data_percentage(), 4.2)

    def testHandlesOptionForTextFileSize(self):
        options, args = self.clp.parse(["--text-file-size=12765"])
        self.failUnlessEqual(args, [])
        self.failUnlessEqual(self.bd.get_text_file_size(), 12765)

    def testHandlesOptionForTextFileSizeWithSuffix(self):
        options, args = self.clp.parse(["--text-file-size=1t"])
        self.failUnlessEqual(args, [])
        self.failUnlessEqual(self.bd.get_text_file_size(), genbackupdata.TiB)

    def testHandlesOptionForBinaryFileSizeWithSuffix(self):
        options, args = self.clp.parse(["--binary-file-size=1t"])
        self.failUnlessEqual(args, [])
        self.failUnlessEqual(self.bd.get_binary_file_size(), 
                             genbackupdata.TiB)

    def testHandlesOptionForCreate(self):
        options, args = self.clp.parse(["--create=1t"])
        self.failUnlessEqual(args, [])
        self.failUnlessEqual(options.create, genbackupdata.TiB)

    def testHandlesOptionForCreateWithRelativeSize(self):
        self.bd.set_preexisting_data_size(12765)
        options, args = self.clp.parse(["--create=10%"])
        self.failUnlessEqual(args, [])
        self.failUnlessEqual(options.create, 1276)

    def testHandlesOptionForDelete(self):
        options, args = self.clp.parse(["--delete=12765"])
        self.failUnlessEqual(args, [])
        self.failUnlessEqual(options.delete, 12765)

    def testHandlesOptionForDeleteWithRelativeCount(self):
        self.bd.set_preexisting_file_count(12765)
        options, args = self.clp.parse(["--delete=10%"])
        self.failUnlessEqual(args, [])
        self.failUnlessEqual(options.delete, 1276)

    def testHandlesOptionForRename(self):
        options, args = self.clp.parse(["--rename=12765"])
        self.failUnlessEqual(args, [])
        self.failUnlessEqual(options.rename, 12765)


if __name__ == "__main__":
    unittest.main()
