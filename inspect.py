import io_netblend.netblend as netblend
from io_netblend.types import all

n = netblend.open(all, 'blend.netblend')

for o in n.walk():
	print(' \033[1;33m' + o.__class__.__name__ + '\033[0m' + ' @ ' + str(id(o)))
	print(o)

print('')
