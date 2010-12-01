# Generate incompressible random data in various ways, and measure speeds.


import random
import gc
import timeit
import hashlib
import zlib


def randint(size):
    """just call random.randint(0, 255)"""
    bytes = []
    for i in range(size):
        bytes.append(chr(random.randint(0, 255)))
    return "".join(bytes)


def getrandbits(size):
    """just call random.getrandbits(8)"""
    bytes = []
    for i in range(size):
        bytes.append(chr(random.getrandbits(8)))
    return "".join(bytes)


def md5ofgetrandbits(size):
    """catenate successive MD5 of random byte stream"""
    chunks = []
    sum = hashlib.md5()
    while size > 0:
        sum.update(chr(random.getrandbits(8)))
        chunk = sum.digest()
        chunks.append(chunk)
        size -= len(chunk)
    if size < 0:
        chunks[-1] = chunks[-1][:size]
    return "".join(chunks)


def md5ofgetrandbits2(size):
    """catenate successive MD5 of random byte stream"""
    chunks = []
    sum = hashlib.md5()
    for i in range(size/16):
        sum.update(chr(random.getrandbits(8)))
        chunk = sum.digest()
        chunks.append(chunk)
    if len(chunks) * 16 < size:
        sum.update(chr(random.getrandbits(8)))
        chunk = sum.digest()
        chunks.append(chunk[:size % 16])
    return "".join(chunks)


def sha1ofgetrandbits(size):
    """catenate successive SHA1 of random byte stream"""
    chunks = []
    sum = hashlib.sha1()
    while size > 0:
        sum.update(chr(random.getrandbits(8)))
        chunk = sum.digest()
        chunks.append(chunk)
        size -= len(chunk)
    if size < 0:
        chunks[-1] = chunks[-1][:size]
    return "".join(chunks)


def sha1ofgetrandbits2(size):
    """catenate successive SHA1 of random byte stream"""
    chunks = []
    sum = hashlib.sha1()
    chunk_size = len(sum.digest())
    for byte in [chr(random.getrandbits(8)) for i in xrange(size / chunk_size)]:
        sum.update(byte)
        chunk = sum.digest()
        chunks.append(chunk)
    if size % chunk_size > 0:
        sum.update(chr(random.getrandbits(8)))
        chunk = sum.digest()
        chunks.append(chunk[:size % chunk_size])
    return "".join(chunks)


def md5ofrandomandstatic(size):
    """MD5 first of random byte stream, then constant"""
    chunks = []
    sum = hashlib.md5()

    initial_size = 128
    while size > 0 and initial_size > 0:
        sum.update(chr(random.getrandbits(8)))
        chunk = sum.digest()
        chunks.append(chunk)
        size -= len(chunk)
    
    while size > 0:
        sum.update("a")
        chunk = sum.digest()
        chunks.append(chunk)
        size -= len(chunk)

    if size < 0:
        chunks[-1] = chunks[-1][:size]

    return "".join(chunks)


def md5ofrandomandstatic2(size):
    """MD5 first of random byte stream, then constant"""
    chunks = []
    sum = hashlib.md5()
    chunk_size = len(sum.digest())

    initial_bytes = min(size, chunk_size * 8)
    for i in range(initial_bytes / chunk_size):
        sum.update(chr(random.getrandbits(8)))
        chunks.append(sum.digest())

    size -= len(chunks) * chunk_size
    for i in range(size / chunk_size):
        sum.update("a")
        chunks.append(sum.digest())

    if size % chunk_size > 0:
        sum.update(chr(random.getrandbits(8)))
        chunks.append(sum.digest()[:size % chunk_size])

    return "".join(chunks)


def sha1ofrandomandstatic2(size):
    """SHA1 first of random byte stream, then constant"""
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


funcs = [
    randint,
    getrandbits, 
    md5ofgetrandbits, 
    md5ofgetrandbits2, 
    sha1ofgetrandbits, 
    sha1ofgetrandbits2, 
    md5ofrandomandstatic,
    md5ofrandomandstatic2,
    sha1ofrandomandstatic2,
    ]


def measure(func, block, count):
    gc.collect()
    timer = timeit.Timer(stmt='%s(%d)' % (func.func_name, block),
                         setup="from __main__ import %s" % func.func_name)
    return min(timer.repeat(repeat=count, number=1))


def check(func, block):
    data = func(block)
    assert len(data) == block, \
           "data is %d bytes, should be %d" % (len(data), block)
    assert len(zlib.compress(data)) >= 0.9 * block, \
           "compressed data is %d bytes, should be at least %d" % \
                (len(zlib.compress(data)), 0.9 * block)


def main():
    block = 1024**2
    count = 10
    print "Measuring %d functions for generating uncompressible binary junk"%\
        len(funcs)
    print "Each function generates %d times %d bytes" % (count, block)
    print "This will take a while"
    print

    namelen = max(len(func.func_name) for func in funcs)

    for func in funcs:
        check(func, block)
        secs = measure(func, block, count)
        speed = block/secs/(1024**2)
        print "%4.1f MB/s %-*s %s" % \
            (speed, namelen, func.func_name, func.__doc__)


if __name__ == "__main__":
    main()
