#!/usr/bin/env python3

from distutils.core import setup
import shutil
import zipfile
import os, os.path

setup(name='netblend',
      version='0.1',
      description='A compact and minimal blend format.',
      author='JacobF',
      author_email='queatz@gmail.com',
      url='http://www.queatz.com/',
      packages=['netblend']
)

shutil.rmtree('io_netblend/netblend', True)
shutil.copytree('netblend', 'io_netblend/netblend')
z = zipfile.ZipFile('NetBlend_Addon.zip', mode = 'w')
for d in os.walk('io_netblend/'):
	z.write(d[0])
	for f in d[2]:
		z.write(os.path.join(d[0], f))
z.close()
