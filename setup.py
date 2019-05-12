from setuptools import setup, find_packages
from os import path

# read the contents of your README file
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

print(find_packages(where='src'))

setup(name='cryptobot',
      version='0.0.1',
      description='Standardized common API for several cryptocurrency exchanges.',
      long_description=long_description,
      long_description_content_type='text/markdown',
      packages=find_packages(),
      install_requires=['requests', 'python-dateutil'],
      tests_require=['pytest']
      )
