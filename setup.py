import os
import sys
from io import open
from distutils.core import setup

# Specify requirements of this package
with open(os.path.join(os.path.dirname(__file__), 'requirements.txt')) as f:
    packages = f.read().splitlines()
    required = []
    private_dependencies = []

    for package in packages:
        if package.startswith('git+ssh:'):
            private_dependencies.append(package)
        else:
            if sys.version_info[0] == 2 or 'futures' not in package:
                # This logic is intended to prevent the futures package from being installed in python 3 environments
                # as it can cause unexpected syntax errors in other packages. Futures is in the standard library in python 3
                # and is should never be installed in these environments.
                # Related: https://github.com/Miserlou/Zappa/issues/1179
                required.append(package)

setup(
    name='order_book',
    version='0.1',
    packages=['order_book', ],
    install_requires=required,
    license='Unlicensed',
    long_description=open('README.md').read(),
)
