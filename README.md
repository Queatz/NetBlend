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
