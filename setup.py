# -*- coding: utf-8 -*-

from __future__ import print_function

import os

from pathlib import Path
from setupbase import (
    log,
    create_cmdclass,
    install_npm,
    combine_commands,
    ensure_targets,
)

from setuptools import setup
from setuptools import find_packages


HERE = Path(__file__).parent
NAME = 'jupyter_require'

ABOUT = dict()
exec(Path(HERE, NAME, '__about__.py').read_text(), ABOUT)

README: str = Path(HERE, "README.rst").read_text(encoding='utf-8')
REQUIREMENTS: list = Path(HERE, 'requirements.txt').read_text().splitlines()

log.set_verbosity(log.DEBUG)
log.info('setup.py entered')
log.info('$PATH=%s' % os.environ['PATH'])

cmdclass = create_cmdclass(
    'js',
    data_files_spec=[
        ('share/jupyter/nbextensions/jupyter-require',
         NAME + '/static',
         '*.js'),
        ('share/jupyter/nbextensions/jupyter-require',
         NAME + '/static',
         '*.js.map'),
        ('etc/jupyter/nbconfig',
         'jupyter-config',
         '**/*.json'),
    ],
)
cmdclass['js'] = combine_commands(
    # FIXME when migrated to node.js
    # install_npm(
    #     path=Path(HERE, 'js'),
    #     build_dir=Path(HERE, NAME, 'static'),
    #     source_dir=Path(HERE, 'js'),
    #     build_cmd='build:all'
    # ),
    ensure_targets([
        NAME + '/static/core.js',  # FIXME when migrated to nodes.js
        NAME + '/static/display.js',  # FIXME when migrated to nodes.js
        NAME + '/static/extension.js',
        # NAME + '/static/index.js',  # FIXME when migrated to nodes.js
    ]),
)


setup(
    name=ABOUT['__title__'],
    version=ABOUT['__version__'],

    author=ABOUT['__author__'],
    author_email=ABOUT['__email__'],
    url=ABOUT['__uri__'],

    license=ABOUT['__license__'],

    description=ABOUT['__summary__'],
    long_description=README,
    long_description_content_type='text/x-rst',

    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Framework :: IPython",
        "Framework :: Jupyter",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Scientific/Engineering :: Visualization",
        "Topic :: Utilities"
    ],

    install_requires=REQUIREMENTS,

    cmdclass=cmdclass,

    packages=find_packages(),
    include_package_data=True,

    zip_safe=False
)
