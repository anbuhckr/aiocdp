#! /usr/bin/env python3

import re
import ast
from setuptools import setup, find_packages

with open('README.md') as readme_file:
    readme = readme_file.read()


_version_re = re.compile(r'__version__\s+=\s+(.*)')


with open('aiocdp/__init__.py', 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1)))


requirements = [    
    'asyncio>=3.4.3',
    'aiohttp>=3.3.2',
    'websockets>=8.1',
]


setup(
    name='aiocdp',
    version=version,
    description="Asynchronous Chrome DevTools Protocol",
    long_description=readme,
    author="anbuhckr",
    author_email='anbu.hckr@hotmail.com',
    url='https://github.com/anbuhckr/aiocdp',
    packages=find_packages(),
    package_dir={},    
    include_package_data=True,
    install_requires=requirements,
    license="GNU GENERAL PUBLIC LICENSE",
    zip_safe=False,
    keywords='aiocdp',
    classifiers=[
        'Development Status :: 1 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: GNU GENERAL PUBLIC LICENSE',
        'Natural Language :: English',       
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Browsers'
    ],
)
