NetBlend
========

A compact and minimal 3D scene format.

Philosophy
----------
NetBlends are compact conglomerates of inter-linkable objects interpreted using a definition list.

NetBlends using the standard definition list are compact 3D scenes that follow the Blender way of doing things.  They are a perfect match for the simplest games that just want to load a set of 3D flora, to advanced games that want to stream high quality, complete scenes and objects over a network.

* **Completeness**
	* No quirks or incompatibilities.  Zip.  None.  It simply works as expected.
	* An extremely simple and easy to use programming interface throughout.
	* What you export is what you get to play with in your game.  If you took the time to create it in your 3D editor, you probably want to be able to use it in your game.
	* It is not only a conversion format; it is perfectly viable to use and edit all objects directly without ever taking them out of the NetBlend.
* **Minimal & Compact**
	* NetBlends consist of a sorted header and a data blob of all objects snugly packed together as bytes.
	* No excess data is stored, only what, optionally you consider, is vital.
	* An empty NetBlend is 0 bytes.
* **Compatible & Extendable**
	* The NetBlend format is universal.  Exporters / Imports can be written for any program.
	* Using the standard definition list, NetBlends never depreciate.
	* NetBlends are made to store any type of custom data.  If certain games need out-of-this-world features it's as simple as creating a custom Type and appending it to the definition list.
	* Use of the standard definition list is entirely optional, in which case the orientation towards storing 3D scenes sums to zero.
* **Chop Chop**
	* Easily export any portions of a scene.
	* Export only features you actually want to use (ex. don't export texcoords of meshes, don't export object names, don't export modifiers, etc.).
	* Objects are chopped up into as many parts as reasonable and acceptable, each stored as individual objects, making all this fancy fancy possible.

How It Works
------------

What makes a NetBlend?  NetBlends consist of a header and a blob of data that is interpreted using a given list of types.

Let's look at the internal structure of a saved NetBlend:

	TYPE COUNT
	TYPE COUNT SIZE SIZE SIZE SIZE
	TYPE COUNT SIZE
	SENTINEL
	DATABLOB

To interpret this, a standard Python list is given along with the NetBlend.  For Example, in the list:

```Python
[Object, Camera, Mesh]
```

Object has a type ID of 1, Camera 2, and Mesh is 3.  Types can either be fixed size or adjustable.  In this example, let's assume Cameras are fixed, and Objects and Meshes are adjustable.

In the above internals, `TYPE` maps to an index in the given list.  Assume the first `TYPE` listed is a Camera. Since Cameras are fixed size, only `COUNT` is written.  This is the number of objects of the `TYPE` in the NetBlend.

Now assume the second `TYPE` is a Mesh.  Meshes can each be different in size, so in addition to writing the `COUNT`, a `SIZE` is written for every object.

Once the `SENTINEL` is reached, all objects have been determined and they begin to be loaded from the `DATABLOB`.

Installing and Using
----------

Simply run

	python3 setup.py install

as superuser to install netblend systemwide and create a .zip of io_netblend which can then be installed through User Preferences in Blender.

If you just want to use the netblend module in your game's source, all you need is the netblend directory.

To read from the netblend, you do something like:

```Python
import netblend

# Import the standard definition set
import netblend.standard

# Open a netblend using the standard definitions list
nb = netblend.open(netblend.standard.defs, 'world.netblend')

# Walk all the objects
for obj in nb.walk():
	print(obj)
```

Creating Custom Types
---------------------

If the data size of the type can very per object, subclass MutableType; if the size is the same for every object, subclass Type.

Types have four methods: size, pack, unpack, and walk.  For fixed-size Type objects, size() is a static method.

`size()` should return the calculated size of the result of pack().  This is so the header can be written before retrieving every object's packed bytes and holding them in memory throughout the save, or pack()ing twice, which is the default if you omit the size() in MutableTypes.

`pack(i)` should return a Python bytes of all the data of the Type that should be saved.  It is supplied one argument, which is a function to convert any object's ID to bytes.

`unpack(b, i)` has two arguments.  The first is the raw bytes (what pack() returned) and the second is a function to convert a section of bytes to a real object.

`walk()` is a method to iterate over all objects this object relies on.

If you want to store more data in a standard type, follow the practice of creating a new Type with a member linking to the standard type (you're just storing the ID in your new Type, not the standard one's data.)

See netblend/standard.py for examples.