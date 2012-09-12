NetBlend
========

A compact and minimal 3D scene format.

Philosophy
----------
NetBlends are compact conglomerates of inter-linkable objects interpreted using a definition list.

NetBlends using the standard definition list are compact 3D scenes that follow the Blender way of doing things.  They are a perfect match for the simplest games that just want to load a set of 3D flora, to advanced games that want to stream high quality, complete scenes and objects over a network.

* **Easy Access to Data**
	* An extremely simple and easy to use programming interface.
	* Opening and fetching any specific data can always be done in a single line of code.
* **Completeness**
	* No quirks or incompatibilities.  Zip.  None.  It simply works as expected.
	* What you export is what you get to play with in your game.  If you took the time to create it in your 3D editor, you probably want to be able to use it in your game.
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

Installing and Using
----------

Simply run

	python3 setup.py build

as superuser to install netblend systemwide and create a .zip of io_netblend which can then be installed through User Preferences in Blender.

If you just want to use the netblend module in your game's source, all you need is the netblend directory.

To read from the netblend, you do something like:

```Python
import netblend

# Find all the models
for obj in netblend.open('world.netblend').find('model'):
	print(obj)
```

You can do the same thing using custom classes:

```Python
import netblend

class Model:
	# This allows it to save correctly
	_nb_type = 'model'

# Find all the models
for obj in netblend.open('world.netblend', {'model': Model}).find(Model):
	print(obj)
```

Creating a netblend from scratch:

```Python
import netblend

nb = NetBlend()
nb.append(netblend.Node())
nb.save('world.netblend')
```
