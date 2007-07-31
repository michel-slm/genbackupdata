#!/usr/bin/python

# Create lots of (empty) files in various ways, to see which way is fastest.


import errno
import gc
import os
import optparse
import shutil
import sys
import timeit


ROOT = "create.tmp"


def create_dir(dirname):
    full_name = os.path.join(ROOT, dirname)
    try:
        os.mkdir(full_name)
    except os.error, e:
        if e.errno != errno.EEXIST:
            raise e
    
def create_file(filename, size):
    full_name = os.path.join(ROOT, filename)
    f = file(full_name, "w")
    f.write("x" * size)
    f.close()
    
def cleanup():
    while os.path.exists(ROOT):
        try:
            shutil.rmtree(ROOT)
        except os.error, e:
            if e.errno != errno.ENOENT:
                raise e
    os.mkdir(ROOT)

def onedir(count, size):
    """All files in one directory"""
    for i in range(count):
        create_file("%d" % i, size)

def subdirsofN(N, count, size):
    prev_subdir = None
    for i in range(count):
        subdir = i / N
        if subdir != prev_subdir:
            create_dir("%d" % subdir)
            prev_subdir = subdir
        create_file("%d/%d" % (subdir, i), size)

def subdirsof100(count, size):
    """Files in subdirs, each with up to 100 files"""
    subdirsofN(100, count, size)

def subdirsof250(count, size):
    """Files in subdirs, each with up to 250 files"""
    subdirsofN(250, count, size)

def subdirsof1000(count, size):
    """Files in subdirs, each with up to 1000 files"""
    subdirsofN(1000, count, size)

def subsubdirsofN(N, count, size):
    prev = None
    for i in range(count):
        subsubdir = i / N
        subdir = subsubdir / N
        if (subdir, subsubdir) != prev:
            create_dir("%d" % subdir)
            create_dir("%d/%d" % (subdir, subsubdir))
            prev_subdir = (subdir, subsubdir)
        create_file("%d/%d/%d" % (subdir, subsubdir, i), size)

def subsubdirsof100(count, size):
    """Files in two-level tree, up to 100 files each"""
    subsubdirsofN(100, count, size)

def subsubdirsof250(count, size):
    """Files in two-level tree, up to 250 files each"""
    subsubdirsofN(250, count, size)

def subsubdirsof1000(count, size):
    """Files in two-level tree, up to 1000 files each"""
    subsubdirsofN(1000, count, size)

funcs = [
    onedir, # disabled, because it exposes a bug in ext3+dir_index
    subdirsof100,
    subdirsof250,
    subdirsof1000,
    subsubdirsof100,
    subsubdirsof250,
    subsubdirsof1000,
    ]

def measure(func, count, size):
    cleanup()
    gc.collect()
    timer = timeit.Timer(stmt='%s(%d, %d)' % (func.func_name, count, size),
                         setup="from __main__ import %s" % func.func_name)
    return timer.timeit(number=1)

def check(func, count, size):
    cleanup()
    func(count, size)
    actual_count = 0
    for dirname, _, filenames in os.walk(ROOT):
        actual_count += len(filenames)
        for name in [os.path.join(dirname, x) for x in filenames]:
            actual_size = os.path.getsize(name)
            assert size == actual_size, \
                   "size is %d, should be %d" % (actual_size, size)
    assert count == actual_count, \
           "count=%d and actual_count=%d should be identical" % \
               (count, actual_count)

def parse_args(args):
    p = optparse.OptionParser()
    
    p.add_option("-c", "--check", action="store_true", default=False,
                 help="Check that all functions actually work")
    p.add_option("-s", "--size", action="store", type="int", metavar="SIZE",
                 default=0, help="Create files of SIZE bytes (default: 0)")
    
    return p.parse_args(args)


def main():
    options, counts = parse_args(sys.argv[1:])
    
    if counts:
        counts = [int(x) for x in counts]
    else:
        counts = [10000]

    for count in counts:
        print "Measuring %d functions for creating %d files of %d bytes" % \
            (len(funcs), count, options.size)
        print
    
        namelen = max(len(func.func_name) for func in funcs)
    
        for func in funcs:
            if options.check:
                check(func, count, options.size)
            secs = measure(func, count, options.size)
            speed = count/secs
            print "%6.0f files/s %-*s %s" % \
                (speed, namelen, func.func_name, func.__doc__)
            sys.stdout.flush()
        print
        print

    cleanup()
    os.rmdir(ROOT)

if __name__ == "__main__":
    main()
