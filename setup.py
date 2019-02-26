from pathlib import Path

from setuptools import find_packages, setup

HERE = Path(__file__).parent

ABOUT = dict()
exec(Path(HERE, 'jupyter_require', '__about__.py').read_text(), ABOUT)

README: str = Path(HERE, "README.md").read_text(encoding='utf-8')
REQUIREMENTS: list = Path(HERE, 'requirements.txt').read_text().splitlines()

setup(
    name=ABOUT['__title__'],
    version=ABOUT['__version__'],

    author=ABOUT['__author__'],
    author_email=ABOUT['__email__'],
    url=ABOUT['__uri__'],

    license=ABOUT['__license__'],

    description=ABOUT['__summary__'],
    long_description=README,
    long_description_content_type='text/markdown',

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

    packages=find_packages(),

    install_requires=REQUIREMENTS,
)
