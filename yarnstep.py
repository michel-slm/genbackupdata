# yarnstep.py -- Python code for making yarn IMPLEMENTS sections nicer
#
# This is meant to be imported, not used with yarn --shell-library.
#
# Copyright 2016  Lars Wirzenius
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
#
# =*= License: GPL-3+ =*=


import os

import cliapp


_next_match = 1
def get_next_match():
    global _next_match
    name = 'MATCH_{}'.format(_next_match)
    _next_match += 1
    return os.environ[name]


def get_next_match_as_int():
    return int(get_next_match())


def get_next_match_as_datadir_path():
    return datadir(get_next_match())


def datadir(relative):
    return os.path.join(os.environ['DATADIR'], relative)


def srcdir(relative):
    return os.path.join(os.environ['SRCDIR'], relative)


def iter_over_files(root):
    for dirname, _, filenames in os.walk(root):
        for filename in filenames:
            yield os.path.join(dirname, filename)


def cat(filename):
    with open(filename) as f:
        return f.read()
