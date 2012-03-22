#! /usr/bin/env python3

# Tool to inspect the contents of a NetBlend.

import netblend

import sys, os

if len(sys.argv) < 2 or not sys.argv[1].strip():
	exit('Usage: inspect.py <file>')

if not os.path.isfile(sys.argv[1]):
	exit('Wrong file')

n = netblend.open(sys.argv[1])

print('')

for o in n.walk():
	print(' \033[1;33m' + o.__class__.__name__ + '\033[0m' + ' @ ' + str(id(o)))
	print(o)

print('')
