from pathlib import Path

from setuptools import find_packages, setup

BASE_DIR = Path(__file__).parent

ABOUT = dict()
exec(Path(BASE_DIR, 'require', '__about__.py').read_text(), ABOUT)

README: str = Path("README.md").read_text()
REQUIREMENTS: list = Path('requirements.txt').read_text().splitlines()

setup(
    name=ABOUT['__title__'],
    version=ABOUT['__version__'],

    author=ABOUT['__author__'],
    author_email=ABOUT['__email__'],
    url=ABOUT['__uri__'],

    license=ABOUT['__license__'],

    description=ABOUT['__summary__'],
    long_description=README,

    classifiers=[
        "Development Status :: 2 - Pre-Alpha"
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License"
    ],

    packages=find_packages(),

    install_requires=REQUIREMENTS,
)