from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='stocklab-twse',
    version='0.6.0',
    description='Stocklab\'s TWSE bundle',

    long_description=long_description,
    long_description_content_type='text/markdown',

    url='https://github.com/hchsiao/stocklab-twse',
    author='Shaun Hsiao',

    packages=find_packages(),

    python_requires='>=3.5',

    install_requires=[
      'stocklab', # clone from: https://github.com/hchsiao/stocklab
      'numpy',
      'scipy',
      'mplfinance',
      'beautifulsoup4',
      'requests',
      'cloudscraper',
      ],
)
