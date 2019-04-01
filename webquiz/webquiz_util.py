#!/usr/bin/env python3
r'''
------------------------------------------------------------------------------
    webquiz_util | utilty functions 
------------------------------------------------------------------------------
    Copyright (C) Andrew Mathas, University of Sydney

    Distributed under the terms of the GNU General Public License (GPL)
                  http://www.gnu.org/licenses/

    This file is part of the WebQuiz system.

    <Andrew.Mathas@sydney.edu.au>
------------------------------------------------------------------------------
'''

import os
import subprocess
import shutil
import stat
import sys
import traceback

# ---------------------------------------------------------------------------------------
# Return the full path for a file in the webquiz directory
webquiz_file = lambda file: os.path.join(os.path.dirname(os.path.realpath(__file__)), file)

def shell_command(cmd):
    r'''
    Short-cut for shell commands
    '''
    return subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True).decode('ascii').strip()

def kpsewhich(search):
    r'''
    Short-cut to access kpsewhich output.

    usage: kpsewhich('-var-value=TEXMFLOCAL')
    '''
    return subprocess.check_output('kpsewhich ' + search, shell=True).decode('ascii').strip()

# ---------------------------------------------------------------------------------------
class MetaData(dict):
    r"""
    A dummy class for reading, accessing and storing key-value pairs from
    a file. Any internal spaces in the key name are replaced with underscores
    and lines without a key-value pair are ignored.

    The key-value pairs are available as both attributes and items

    Usage: MetaData(filename) or MetaData(filename, key-value pairs)
    """

    def __init__(self, filename, **args):
        dict.__init__(self)
        # add attributes from **args
        for key in args:
            setattr(self, key, args[key])
        with open(filename, 'r') as meta:
            for line in meta:
                if '=' in line:
                    key, val = line.strip().split('=')
                    if key.strip() != '':
                        self.__setitem__(key.strip().lower().replace(' ', '_'),
                                         val.strip())
                        setattr(self,
                                key.strip().lower().replace(' ', '_'),
                                val.strip())


#################################################################################
def webquiz_debug(debugging, *arg):
    if debugging:
        sys.stderr.write(' '.join('{}'.format(a) for a in arg)+'\n')


#################################################################################
def webquiz_error(debugging, msg, err=None):
    r'''
    Consistent handling of errors in magthquiz: print the message `msg` and
    exist with error code `err.errno` if it is available.abs
    '''
    print('{dash}WebQuiz error:\n  {msg}\n{dash}'.format(
           msg=msg, dash='-'*40+'\n')
    )

    if err is not None:
        trace = traceback.extract_tb(sys.exc_info()[2])
        filename, lineno, fn, text = trace[-1]
        print('File: {}, line number: {}\nError {} in {}: {}'.format(
            filename, lineno, err, fn, text))

    if debugging and err is not None:
        raise

    if hasattr(err, 'errno'):
        sys.exit(err.errno)

    sys.exit(1)


###############################################################################
def copytree(src, dst, symlinks=False, ignore=None):
    r''' Recursively copy directory tree, fixing shutil.copytree
         from https://stackoverflow.com/questions/1868714
    '''
    if not os.path.exists(dst):
        os.makedirs(dst)
        shutil.copystat(src, dst)
    lst = os.listdir(src)
    if ignore:
        excl = ignore(src, lst)
        lst = [x for x in lst if x not in excl]
    for item in lst:
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if symlinks and os.path.islink(s):
            if os.path.lexists(d):
                os.remove(d)
            os.symlink(os.readlink(s), d)
            try:
                st = os.lstat(s)
                mode = stat.S_IMODE(st.st_mode)
                os.lchmod(d, mode)
            except OSError:
                pass  # lchmod not available
        elif os.path.isdir(s):
            copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)

###############################################################################
## shortcuts for running commands
environ = os.environ.copy()

def run(cmd, shell=False):
    r'''
    Run commands with output to stdout and errors to stderr
    '''
    if shell:
        subprocess.call(cmd, env=environ, shell=True)
    else:
        subprocess.call(cmd.split(), env=environ)

def quiet_run(cmd, shell=False):
    r'''
    Run commands with ignoring and sending errors to stderr
    '''
    if shell:
        subprocess.call(cmd, env=environ, stdout=open(os.devnull, 'wb'), shell=True)
    else:
        subprocess.call(cmd.split(), env=environ, stdout=open(os.devnull, 'wb'))

def silent_run(cmd, shell=False):
    r'''
    Run commands ignoring all output and errors
    '''
    if shell:
        subprocess.call(cmd, env=environ, stdout=open(os.devnull, 'wb'), stderr=open(os.devnull, 'wb'), shell=True)
    else:
        subprocess.call(cmd.split(), env=environ, stdout=open(os.devnull, 'wb'), stderr=open(os.devnull, 'wb'))
