from distutils.core import setup
from setuptools import find_packages

setup(
    name='minivc',
    version='0.1.04',
    author='Nathan ToddStone',
    author_email='me@nathants.com',
    packages=find_packages(),
    scripts=['bin/mvc'],
    url='http://github.com/nathants/minivc',
    license='LICENSE.txt',
    description='a minimal mvc library, with zero frameworks attached.',
    long_description=open('README.rst').read(),
    install_requires=open('pip.txt').readlines(),
)