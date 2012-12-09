"""
Shim that provides Python 2.6 (and later) programs with some features
of the subprocess module introduced in later Python versions.

Requires:
* Python 2.6 or later
"""

# Everything in current version of subprocess
from subprocess import *

# Python 2.7 extensions
try:
    from subprocess import check_output
except:
    def check_output(*popenargs, **kwargs):
        if 'stdout' in kwargs:
            raise ValueError('stdout argument not allowed, it will be overridden.')
        process = Popen(stdout=PIPE, *popenargs, **kwargs)
        output, unused_err = process.communicate()
        retcode = process.poll()
        if retcode:
            cmd = kwargs.get("args")
            if cmd is None:
                cmd = popenargs[0]
            raise CalledProcessError(retcode, cmd, output=output)
        return output

# Python 3.3 extensions
try:
    from subprocess import DEVNULL
except:
    import os
    DEVNULL = open(os.devnull, 'rwb')