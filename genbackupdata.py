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


import hashlib
import optparse
import os
import random
import sys


KiB = 2 ** 10   # A kibibyte
MiB = 2 ** 20   # A mebibyte
GiB = 2 ** 30   # A gibibyte
TiB = 2 ** 40   # A tebibyte

# Defaults for various settings in the BackupData class.
DEFAULT_SEED = 0
DEFAULT_BINARY_CHUNK_SIZE = KiB
DEFAULT_TEXT_FILE_SIZE = 10 * KiB
DEFAULT_BINARY_FILE_SIZE = 10 * MiB
DEFAULT_TEXT_DATA_PERCENTAGE = 10.0
DEFAULT_MAX_FILES_PER_DIRECTORY = 256
DEFAULT_MODIFY_PERCENTAGE = 10

# Random filler text for generating text data.
if True: #pragma: no cover:
    LOREM_IPSUM = """
Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod
tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim
veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea
commodo consequat. Duis aute irure dolor in reprehenderit in voluptate
velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint
occaecat cupidatat non proident, sunt in culpa qui officia deserunt
mollit anim id est laborum.
"""


class BackupData:

    """This class represents the directory with backup data"""
    
    def __init__(self):
        self._dirname = None
        self._seed = 0
        self._prng = None
        self._chunk_size = DEFAULT_BINARY_CHUNK_SIZE
        self._text_file_size = DEFAULT_TEXT_FILE_SIZE
        self._binary_file_size = DEFAULT_BINARY_FILE_SIZE
        self._text_data_percentage = DEFAULT_TEXT_DATA_PERCENTAGE
        self._max_files_per_directory = DEFAULT_MAX_FILES_PER_DIRECTORY
        self._modify_percentage = DEFAULT_MODIFY_PERCENTAGE
        self._preexisting_file_count = 0
        self._preexisting_data_size = 0
        self._filename_counter = 0
        self._current_dir_no = 0
        self._next_filecount = 0
        
        # The zlib compression algorithm gives up if it gets a block of
        # 32 KiB bytes it can't find in its dictionary. It completely
        # ignores such a block, meaning that if it is repeated, then
        # it ignores it repeatedly. Most importantly for us, it doesn't
        # compress the repeats, either. Thus, to generate lots of
        # uncompressible binary data, we can generate a blob and repeat
        # that. Thanks to Richard Braakman for the idea.
        self._binary_blob_size = 64 * 1024 # Safety factor of 2
        self._binary_blob = None

    def set_directory(self, dirname):
        """Set the directory to be operated on
        
        Note that this must be set exactly once. Setting it twice will cause
        an assertion error, and not setting it will cause other errors.
        
        """
        
        assert self._dirname is None
        self._dirname = dirname
        
    def get_directory(self):
        """Return the directory being operated on, or None if not set"""
        return self._dirname
        
    def create_directory(self):
        """Create the backup data directory, if it doesn't exist already"""
        if not os.path.exists(self._dirname):
            os.mkdir(self._dirname)

    def get_seed(self):
        """Return the initial seed for the pseudo-random number generator"""
        return self._seed
        
    def set_seed(self, seed):
        """Set the initial seed for the pseudo-random number generator
        
        The seed will be used when the generator is first initialized.
        It is initialized implicitly as soon as something in this class
        needs randomness. Setting the seed after the generator has been
        initialized causes an assertion failure.
        
        """

        assert self.get_prng() is None
        self._seed = seed

    def get_prng(self):
        """Return reference to the psuedo-random number generator being used
        
        Return None, if one hasn't be initialized yet.
        
        """
        
        return self._prng
        
    def init_prng(self):
        """Initialize the psuedo-random number generator (using seed)"""
        if self._prng is None:
            self._prng = random.Random()
            self._prng.seed(self._seed)

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

    def get_max_files_per_directory(self):
        """Return current setting of maximum number of files per directory"""
        return self._max_files_per_directory

    def set_max_files_per_directory(self, count):
        """Set maximum number of files per directory"""
        self._max_files_per_directory = count

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
        count = 0
        size = 0
        if os.path.exists(self._dirname):
            for root, dirs, filenames in os.walk(self._dirname):
                count += len(filenames)
                for filename in filenames:
                    size += os.path.getsize(os.path.join(root, filename))
        self.set_preexisting_file_count(count)
        self.set_preexisting_data_size(size)

    def _choose_directory(self):
        """Choose directory in which to create the next file"""
        
        while True:
            dirname = os.path.join(self._dirname, 
                                   "dir%d" % self._current_dir_no)
            if not os.path.exists(dirname):
                self._next_filecount = 0
                break
            if (self._next_filecount > 0 and
                self._next_filecount < self._max_files_per_directory):
                break
            self._current_dir_no += 1
        return dirname
        
    def next_filename(self):
        """Choose the name of the next filename
        
        The file does not currently exist. This is not, however, a guarantee
        that no other process won't create it before we do. Thus, this
        is NOT a secure way to create temporary files. But it's good enough
        for our intended purpose.
        
        For simplified unit testing, the names are very easily predictable,
        but it is probably a bad idea for external code to rely on this.
        
        """

        dirname = self._choose_directory()
        while True:
            filename = os.path.join(dirname, 
                                    "file%d" % self._filename_counter)
            if not os.path.exists(filename):
                self._next_filecount += 1
                return filename
            self._filename_counter += 1

    def generate_text_data(self, size):
        """Generate SIZE characters of text data"""
        if size <= len(LOREM_IPSUM):
            return LOREM_IPSUM[:size]
        else:
            full = size / len(LOREM_IPSUM)
            rest = size % len(LOREM_IPSUM)
            return "".join(([LOREM_IPSUM] * full) + [LOREM_IPSUM[:rest]])

    def generate_binary_data_well(self, size):
        """Generate SIZE bytes of more or less random binary junk"""
        
        # The following code has had some fine manual fine tuning done
        # to it. This has made it a bit ugly, but faster. On a 
        # "Intel(R) Core(TM)2 Duo CPU L9400 @ 1.86GHz", it produces
        # about 25 MB/s.

        chunks = []
        sum = hashlib.sha1()
        chunk_size = len(sum.digest())

        initial_bytes = min(size, 128)
        for i in range(initial_bytes / chunk_size):
            sum.update(chr(random.getrandbits(8)))
            chunk = sum.digest()
            chunks.append(chunk)

        size -= len(chunks) * chunk_size
        for i in range(size / chunk_size):
            sum.update("a")
            chunk = sum.digest()
            chunks.append(chunk)

        if size % chunk_size > 0:
            sum.update(chr(random.getrandbits(8)))
            chunk = sum.digest()
            chunks.append(chunk[:size % chunk_size])

        return "".join(chunks)


    def generate_binary_data(self, size):
        """Generate SIZE bytes of binary junk.
        
        This is different from generate_binary_data_well in that
        it makes use of _binary_blob (and generates that if it does
        not yet exist).
        
        """
        
        if self._binary_blob is None:
            self._binary_blob = self.generate_binary_data_well(
                                    self._binary_blob_size)
        if size <= len(self._binary_blob):
            return self._binary_blob[:size]
        else:
            full = size / len(self._binary_blob)
            rest = size % len(self._binary_blob)
            return "".join(([self._binary_blob] * full) + 
                           [self._binary_blob[:rest]])

    def create_subdirectories(self, filename):
        """Create the sub-directories that are needed to create filename"""
        subdir = os.path.dirname(filename)
        if not os.path.exists(subdir):
            os.makedirs(subdir)

    def create_text_file(self, size):
        """Create a new text file of the desired size"""
        filename = self.next_filename()
        self.create_subdirectories(filename)
        f = file(filename, "w")
        f.write(self.generate_text_data(size))
        f.close()

    def get_binary_chunk_size(self):
        """Return the size of chunks used when writing binary data"""
        return self._chunk_size

    def set_binary_chunk_size(self, size):
        """Set the size of chunks used when writing binary data"""
        self._chunk_size = size

    def create_binary_file(self, size):
        """Create a new binary file of the desired size"""
        filename = self.next_filename()
        self.create_subdirectories(filename)
        f = file(filename, "w")
        # We write the data in chunks, so as not to keep the entire file
        # contents in memory at a time. Since the size may be very large,
        # we might otherwise run out of swap.
        while size >= self._chunk_size:
            f.write(self.generate_binary_data(self._chunk_size))
            size -= self._chunk_size
        f.write(self.generate_binary_data(size))
        f.close()

    def _create_files_of_a_kind(self, size, file_size, create_one):
        """Create files with create_one"""
        while size > 0:
            this_size = min(size, file_size)
            create_one(this_size)
            size -= this_size

    def create_files(self, size):
        """Create new files, totalling SIZE bytes in size"""
        text_size = int(0.01 * self._text_data_percentage * size)
        bin_size = size - text_size

        self._create_files_of_a_kind(text_size, self.get_text_file_size(),
                                     self.create_text_file)
        self._create_files_of_a_kind(bin_size, self.get_binary_file_size(),
                                     self.create_binary_file)

    def find_files(self):
        """Find all non-directory files in the test data set"""
        files = []
        for root, dirs, filenames in os.walk(self._dirname):
            for filename in filenames:
                files.append(os.path.join(root, filename))
        return files

    def choose_files_randomly(self, count):
        """Choose COUNT files randomly"""
        files = self.find_files()
        if len(files) >= count:
            self.init_prng()
            files = self._prng.sample(files, count)
        return files

    def delete_files(self, count):
        """Delete COUNT files"""
        if os.path.exists(self._dirname):
            for file in self.choose_files_randomly(count):
                os.remove(file)

    def rename_files(self, count):
        """Rename COUNT files to new names"""
        if os.path.exists(self._dirname):
            for file in self.choose_files_randomly(count):
                new_file = self.next_filename()
                self.create_subdirectories(new_file)
                os.rename(file, new_file)

    def link_files(self, count):
        """Create COUNT new filenames that are hard links to existing files"""
        if os.path.exists(self._dirname):
            for file in self.choose_files_randomly(count):
                new_file = self.next_filename()
                self.create_subdirectories(new_file)
                os.link(file, new_file)

    def get_modify_percentage(self):
        """Return how many percent to grow each file with modify_files()"""
        return self._modify_percentage
        
    def set_modify_percentage(self, percent):
        """Set how many percent to grow each file with modify_files()"""
        self._modify_percentage = percent

    def append_data(self, filename, data):
        """Append data to a file"""
        f = file(filename, "a")
        f.write(data)
        f.close()

    def _modify_files_of_a_kind(self, filenames, size, generate_data):
        """Modify files by appending data to them"""
        while size > 0:
            filename = self._prng.choice(filenames)
            this_size = os.path.getsize(filename)
            amount = min(int(0.01 * self._modify_percentage * this_size),
                         size)
            self.append_data(filename, generate_data(amount))
            size -= amount

    def modify_files(self, size):
        """Modify existing files by appending to them
        
        SIZE gives the total amount of new data for all files.
        Files are chosen at random, and new data is appended to them.
        The amount appended to each file is set by
        set_modify_percentage. The data is split between text and
        binary data according to set_text_data_percentage.
        
        """
        
        if os.path.exists(self._dirname):
            files = self.find_files()

            text_size = int(0.01 * self._text_data_percentage * size)
            bin_size = size - text_size

            self.init_prng()
            self._modify_files_of_a_kind(files, text_size, 
                                         self.generate_text_data)
            self._modify_files_of_a_kind(files, bin_size, 
                                         self.generate_binary_data)



class CommandLineParser:

    """Parse the command line for the genbackupdata utility"""
    
    def __init__(self, backup_data):
        self._bd = backup_data
        self._parser = self._create_option_parser()

    def _create_option_parser(self):
        """Create the OptionParser we need"""
        
        p = optparse.OptionParser()

        p.add_option("--seed",
                     help="Set pseudo-random number generator seed to SEED")

        p.add_option("--max-count",
                     action="store",
                     metavar="COUNT",
                     help="Allow at most COUNT files per directory")

        p.add_option("-p", "--percentage-text-data",
                     action="store",
                     metavar="PERCENT",
                     help="Make PERCENT of new data textual, not binary")

        p.add_option("-t", "--text-file-size",
                     action="store",
                     metavar="SIZE",
                     help="Make new text files be of size SIZE")

        p.add_option("-b", "--binary-file-size",
                     action="store",
                     metavar="SIZE",
                     help="Make new binary files be of size SIZE")

        p.add_option("-c", "--create",
                     action="store",
                     metavar="SIZE",
                     help="Create SIZE amount of new files")

        p.add_option("-d", "--delete",
                     action="store",
                     metavar="COUNT",
                     help="Delete COUNT files")

        p.add_option("-r", "--rename",
                     action="store",
                     metavar="COUNT",
                     help="Rename COUNT files")

        p.add_option("-l", "--link",
                     action="store",
                     metavar="COUNT",
                     help="Create COUNT new hard links")

        p.add_option("-m", "--modify",
                     action="store",
                     metavar="SIZE",
                     help="Grow total data size by SIZE")

        p.add_option("--modify-percentage",
                     action="store",
                     metavar="PERCENT",
                     help="Increase file size by PERCENT")

        return p

    def parse_size(self, size, base_size=None):
        """Parse a SIZE argument (absolute, relative, with/without suffix)"""
        
        suffixes = (("k", KiB), ("m", MiB), ("g", GiB), ("t", TiB))

        for suffix, factor in suffixes:
            if size.lower().endswith(suffix):
                return int(float(size[:-len(suffix)]) * factor)

        if size.endswith("%"):
            if base_size is None:
                return 0
            else:
                return int(float(size[:-1]) * 0.01 * base_size)

        return int(size)

    def parse_count(self, count, base_count=None):
        """Parse a COUNT argument (absolute, relative, with/without suffix)"""
        
        suffixes = (("k", 10**3), ("m", 10**6), ("g", 10**9), ("t", 10**12))

        for suffix, factor in suffixes:
            if count.lower().endswith(suffix):
                return int(float(count[:-len(suffix)]) * factor)

        if count.endswith("%"):
            if base_count is None:
                return 0
            else:
                return int(float(count[:-1]) * 0.01 * base_count)

        return int(count)

    def parse(self, args):
        """Parse command line arguments"""
        options, args = self._parser.parse_args(args)
            
        if len(args) == 1:
            self._bd.set_directory(args[0])
            self._bd.find_preexisting_files()
        
        if options.seed:
            self._bd.set_seed(int(options.seed))
        
        if options.max_count:
            self._bd.set_max_files_per_directory(int(options.max_count))
        
        if options.percentage_text_data:
            self._bd.set_text_data_percentage(
                float(options.percentage_text_data))
        
        if options.modify_percentage:
            self._bd.set_modify_percentage(float(options.modify_percentage))

        if options.text_file_size:
            self._bd.set_text_file_size(
                self.parse_size(options.text_file_size))

        if options.binary_file_size:
            self._bd.set_binary_file_size(
                self.parse_size(options.binary_file_size))

        if options.create:
            options.create = self.parse_size(options.create, 
                                        self._bd.get_preexisting_data_size())

        if options.modify:
            options.modify = self.parse_size(options.modify, 
                                        self._bd.get_preexisting_data_size())

        if options.delete:
            options.delete = self.parse_count(options.delete, 
                                        self._bd.get_preexisting_file_count())

        if options.rename:
            options.rename = self.parse_count(options.rename, 
                                        self._bd.get_preexisting_file_count())

        if options.link:
            options.link = self.parse_count(options.link, 
                                        self._bd.get_preexisting_file_count())

        return options, args


class AppException(Exception):

    def __str__(self):
        return self._str
        
        
class NeedExactlyOneDirectoryName(AppException):

    def __init__(self):
        self._str = ("Need exactly one command line argument, "
                     "giving directory name")


class Application:

    """The main program"""
    
    def __init__(self, args):
        self._args = args
        self._bd = BackupData()
        self._clp = CommandLineParser(self._bd)
        self._error = sys.stderr.write

    def set_error_writer(self, writer):
        self._error = writer

    def run(self):
        """Execute the desired operations"""
        try:
            options, args = self._clp.parse(self._args)

            if len(args) != 1:
                raise NeedExactlyOneDirectoryName()
            
            if options.delete:
                self._bd.delete_files(options.delete)
            
            if options.rename:
                self._bd.rename_files(options.rename)
            
            if options.link:
                self._bd.link_files(options.link)
            
            if options.modify:
                self._bd.modify_files(options.modify)
            
            if options.create:
                self._bd.create_files(options.create)

        except AppException, e:
            self._error(str(e) + "\n")
            sys.exit(1)


if __name__ == "__main__": #pragma: no cover
    Application(sys.argv[1:]).run()
