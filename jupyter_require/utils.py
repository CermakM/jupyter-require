# jupyter-require
# Copyright 2019 Marek Cermak <macermak@redhat.com>
#
# MIT License
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Other useful utilities."""

import logging
import daiquiri

import shlex
import subprocess

from typing import Union

from IPython.core.display import display
from IPython.core.display import Javascript

logger = daiquiri.getLogger()


# These utilities are useful for handling jupyter-require nbextension,
# when communication can not yet be handled by the jupyter-require itself.

_NBEXTENSION = 'jupyter-require'


def install_nbextension(extension: str,
                        *flags,
                        py=True,
                        sys_prefix=True,
                        symlink=False,
                        overwrite=True,
                        config: str = '',
                        log_level: Union[int, str] = logging.INFO):
    """Install nbextension.

    :param extension: path to the extension or Python package name (if py=True)
    :param py: bool, Whether to install from Python package (default: True)
    :param sys_prefix: bool, Whether to use sys prefix, use this in virtual envs (default: True)
    :param symlink: bool, Whether to create symlink to package data (default: False)
    :param overwrite:  bool, Whether to overwrite current files (default: True)
    :param config:  str, full path to a config file
    :param log_level:  enum, application log level
    :param flags: str, additional flags
    """
    version = subprocess.check_output(
        args=shlex.split("jupyter nbextension --version"),
        stderr=subprocess.STDOUT,
        universal_newlines=True,
    )

    logger.debug("Jupyter nbextension version: %s", version.strip())

    install_cmd = "jupyter nbextension install"

    opts = ''
    opts += ' --py' if py else ''
    opts += ' --sys-prefix' if sys_prefix else ''
    opts += ' --symlink' if symlink else ''
    opts += ' --overwrite' if overwrite else ''

    args = ''
    args += f' --config {config}' if config else ''
    args += f' --log-level {log_level}'

    flags = ' '.join(flags)

    cmd = ' '.join([install_cmd, opts, args, flags, extension])

    p = subprocess.Popen(
        args=shlex.split(cmd),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
    )

    logger.debug("Installing extension: %s", extension)

    out, err = p.communicate(timeout=60)

    logger.info(out)
    if err:
        logger.error(err)

    logger.debug("Success.")

    return p.returncode


def _enable_nbextension():
    """Enable jupyter-require nbextension."""
    script = f"""
    Jupyter.notebook.config.update({{
        'load_extensions': {{
            '{_NBEXTENSION}': true
        }}
    }});
    """

    return display(Javascript(script))


def _disable_nbextension():
    """Disable jupyter-require nbextension."""
    script = f"""
    Jupyter.notebook.config.update({{
        'load_extensions': {{
            '{_NBEXTENSION}': true
        }}
    }});
    """

    return display(Javascript(script))


def _load_nbextension(enable=True):
    """Load and enable jupyter-require nbextension.

    Note: The jupyter-require nbextension has to be installed first.
    """
    script = f"""
    require(['base/js/utils'], (utils) => {{
        utils.load_extensions('{_NBEXTENSION}/extension')
    }});
    """

    if enable:
        _enable_nbextension()

    return display(Javascript(script))

