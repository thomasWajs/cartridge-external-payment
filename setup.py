from distutils.core import setup
from setuptools import find_packages

setup(
    name='cartridge-external-payment',
    version='0.0.1',
    author='Thomas Wajs',
    author_email='thomas.wajs@gmail.com',
    packages=find_packages(),
    scripts=[],
    url='http://pypi.python.org/pypi/cartridge-external-payment/',
    license='LICENSE.txt',
    description='A module for Cartridge that manage payment on externak platform.',
    long_description=open('README.md').read(),
    install_requires=[
        "cartridge >= 0.6.0",
    ],
    include_package_data=True,
    zip_safe=False,
)
