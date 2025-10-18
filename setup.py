#!/usr/bin/env python

from setuptools import setup

import pyhosts

setup(name="pyhosts",
      version="0.1.0",
      description="Pythonic way to manage hosts file.",
      author="Igor Milovanovic",
      author_email="igor@tnkng.com",
      url="https://github.com/igormilovanovic/pyhosts/",
      packages=['pyhosts'],
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.8',
          'Programming Language :: Python :: 3.9',
          'Programming Language :: Python :: 3.10',
          'Programming Language :: Python :: 3.11',
          'Programming Language :: Python :: 3.12',
      ],
      python_requires='>=3.8',
      )
