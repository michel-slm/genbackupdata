from distutils.core import setup

setup(name='genbackupdata',
      version='1.2',
      description='Generate test data for backup software',
      long_description='''\
genbackupdata creates or modifies directory trees in ways that simulate
real filesystems sufficiently well for performance testing of backup
software. For example, it can create files that are a mix of small text
files and big binary files, with the binary files containing random
binary junk which compresses badly. This can then be backed up, and
later the directory tree can be changed by creating new files, modifying
files, or deleting or renaming files. The backup can then be run again.

The output is deterministic, such that for a given set of parameters the
same output always happens. Thus it is more efficient to distribute
genbackupdata and a set of parameters between people who wish to
benchmark backup software than distributing very large test sets.
''',
      author='Lars Wirzenius',
      author_email='liw@iki.fi',
      url='http://braawi.org/genbackupdata.html',
      classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Testing',
        'Topic :: System :: Archiving :: Backup',
      ],
      license='GNU General Public License, version 2 or later',
      py_modules=['genbackupdata'],
      scripts=['genbackupdata'],
     )
