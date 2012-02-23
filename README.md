NetBlend
========

A compact and minimal blend format.

How It Works
------------

What makes a NetBlend?  NetBlends consist of a header and a blob of data that is interpreted using a given list of types.

Let's look at the internal structure of a saved NetBlend:

	TYPE COUNT
	TYPE COUNT
	SIZE
	SIZE
	SIZE
	SIZE
	TYPE COUNT
	SENTINEL
	DATABLOB

To interpret this, a standard Python list is given along with the NetBlend.  For Example, in the list:

	[Object, Camera, Mesh]

Object has a type ID of 1, Camera 2, and Mesh is 3.  Types can either be fixed size or adjustable.  In this example, let's assume Cameras are fixed, and Objects and Meshes are adjustable.

In the above internals, TYPE maps to an index in the given list.  Assume the first TYPE listed is a Camera. Since Cameras are fixed size, only COUNT is written.  This is the number of objects of the TYPE in the NetBlend.

Now assume the second type is a Mesh.  Meshes can each be different in size, so in addition to writing the COUNT, a SIZE is written for every object.

Once the sentinel is reached, all objects have been determined and they begin to be loaded from the DATABLOB.

Installing
----------

Simply run

	sudo python3 setup.py install

to install netblend systemwide and create a .zip of io_netblend which can then be installed through User Preferences.

To read from the netblend, you do something like:

	import netblend
	
	# Import the standard definition set
	import netblend.standard

	# Open a netblend using the standard definitions list
	nb = netblend.open(netblend.standard.defs, 'world.netblend')
	
	# Walk all the objects
	for obj in nb.walk():
		print(obj)

Creating Custom Types
---------------------

If the data size of the type can very per object, subclass MutableType; if the size is the same for every object, subclass Type.

Types have four methods: size, pack, unpack, and walk.  For fixed-size Type objects, size() is a static method.

size() should return the calculated size of the result of pack().  This is so the header can be written before retrieving every object's packed bytes and holding them in memory throughout the save, or pack()ing twice.

pack(i) should return a Python bytes of all the data of the Type that should be saved.  It is supplied one argument, which is a function to convert any object's ID to bytes.

unpack(b, i) has two arguments.  The first is the raw bytes (what pack() returned) and the second is a function to convert a section of bytes to a real object.

walk() is a method to iterate over all objects this object relies on.

See netblend/standard.py for examples.
