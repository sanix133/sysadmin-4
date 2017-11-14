#!/usr/bin/env python

import glob
import os
import shutil
import subprocess
import sys

from setuptools import setup

from distutils.command.build import build as _build
from distutils.command.clean import clean as _clean
from distutils.spawn import find_executable


with open('requirements.txt', 'r') as requirements_file:
    REQUIREMENTS = list(requirements_file)

with open('dev-requirements.txt', 'r') as dev_requirements_file:
    DEV_REQUIREMENTS = list(dev_requirements_file)


if 'PROTOC' in os.environ and os.path.exists(os.environ['PROTOC']):
    protoc = os.environ['PROTOC']
else:
    protoc = find_executable('protoc')


def generate_proto(source_file, generated_dir):
    print "Generating %s" % source_file
    if not os.path.exists(source_file):
        print >>sys.stderr, "Can't find required file: %s" % source_file
        sys.exit(-1)
    if protoc is None:
        print >>sys.stderr, "protoc could not be found. Please install it"
        sys.exit(-1)
    if not os.path.exists(generated_dir):
        os.makedirs(generated_dir)
        open(os.path.join(generated_dir, '__init__.py'), 'w+').close()
    protoc_command = [protoc,
                      '-I../../sysadmin-api',
                      "--python_out=%s" % generated_dir,
                      source_file]
    if subprocess.call(protoc_command) != 0:
        sys.exit(-1)


def clean_command(generated_dir):
    class Clean(_clean):
        def run(self):
            if os.path.exists(generated_dir):
                print 'rm -rf %s' % generated_dir
                shutil.rmtree(generated_dir)
    return Clean


def build_command(generated_dir):
    class Build(_build):
        def run(self):
            for proto_file in glob.glob(os.path.join("../../sysadmin-api",
                                                     "*.proto")):
                generate_proto(proto_file, generated_dir)
            _build.run(self)
    return Build


GENERATED_DIR = os.path.join('sysadmin', 'generated')

setup(
    name='sysadmin',
    version='1.0.1',
    description='Control sysadmin',
    install_requires=REQUIREMENTS,
    extras_require={'test': DEV_REQUIREMENTS},
    cmdclass={
        'build': build_command(GENERATED_DIR),
        'clean': clean_command(GENERATED_DIR),
    },
    packages=[
        'sysadmin',
        'sysadmin.generated'
    ],
    scripts=[
        'sysadminctl',
        'templater.py',
        'gen-factory-settings.py',
        'migrate.py',
    ],
    classifiers=[
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7'
    ]
  )
