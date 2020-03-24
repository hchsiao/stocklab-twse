from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='stocklab',
    version='0.1.1',
    description='A modular python programming interface to access financial data from various sources.',

    long_description=long_description,
    long_description_content_type='text/markdown',

    url='https://github.com/syoukore/stocklab',

    author='syoukore',

    # When your source code is in a subdirectory under the project root, e.g.
    # `src/`, it is necessary to specify the `package_dir` argument.
    #package_dir={'': 'src'},  # Optional

    # You can just specify package directories manually here if your project is
    # simple. Or you can use find_packages().
    #
    # Alternatively, if you just want to distribute a single Python file, use
    # the `py_modules` argument instead as follows, which will expect a file
    # called `my_module.py` to exist:
    #
    #   py_modules=["my_module"],
    #
    packages=find_packages(where='.'),  # Required

    python_requires='>=3.5',

    install_requires=[
        'numpy',
        'scipy',
        'mpl_finance',
        'beautifulsoup4',
        'requests',
        'cloudscraper',
        'pyDAL',
        ],
)
