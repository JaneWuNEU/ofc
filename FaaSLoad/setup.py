#!/usr/bin/env python3

# Example setup.py from https://github.com/navdeep-G/setup.py
# For Pipenv configuration vs. setup.py: https://github.com/pypa/pipenv/issues/1911

import io
import os

from setuptools import find_packages, setup

# Package meta-data.
NAME = 'faasload'
DESCRIPTION = 'Load injector to FaaS platform'
URL = None
EMAIL = 'mathieu.bacou@telecom-sudparis.eu'
AUTHOR = 'Mathieu Bacou'
REQUIRES_PYTHON = '>=3.6.0'
VERSION = '0.1.0'

# What packages are required for this module to be executed?
REQUIRED = [
    'mysql-connector-python', 'pyyaml', 'kafka-python'
]
# plus local pywhisk and pycgroup
# Note related to Pipfile: the dependencies from REQUIRED will **not** appear in the Pipfile. The latter only contains
# the project itself, but the project is installed via setup.py which pulls its runtime dependencies. The dependencies
# do appear in the Pipfile.lock. At any rate, Pipfile nor Pipfile.lock should be checked in to Git.

# What packages are optional?
# Can be used to include dependencies for tests only
EXTRAS = {
    # 'fancy feature': ['django'],
}

# The rest you shouldn't have to touch too much :)
# ------------------------------------------------
# Except, perhaps the License and Trove Classifiers!
# If you do change the License, remember to change the Trove Classifier for that!

here = os.path.abspath(os.path.dirname(__file__))

# Import the README and use it as the long-description.
# Note: this will only work if 'README.md' is present in your MANIFEST.in file!
try:
    with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
        long_description = '\n' + f.read()
except FileNotFoundError:
    long_description = DESCRIPTION

# Load the package's __version__.py module as a dictionary.
about = {}
if not VERSION:
    project_slug = NAME.lower().replace("-", "_").replace(" ", "_")
    with open(os.path.join(here, project_slug, '__version__.py')) as f:
        exec(f.read(), about)
else:
    about['__version__'] = VERSION

# Where the magic happens:
setup(
    name=NAME,
    version=about['__version__'],
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type='text/markdown',
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    packages=find_packages(exclude=["tests", "*.tests", "*.tests.*", "tests.*"]),
    # If your package is a single module, use this instead of 'packages':
    # py_modules=['client'],
    entry_points={},
    install_requires=REQUIRED,
    extras_require=EXTRAS,
    include_package_data=True,
    license='',
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
    ],
)
