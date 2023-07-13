from random import sample
from para import server_size, client_size, intersection_size
import os


#set elements can be integers < order of the generator of the elliptic curve (192 bits integers if P192 is used); 'sample' works only for a maximum of 63 bits integers.
disjoint_union = sample(range(2 ** 63 - 1), server_size + client_size)
intersection = disjoint_union[:intersection_size]
server_set = intersection + disjoint_union[intersection_size: server_size]
client_set = intersection + disjoint_union[server_size: server_size - intersection_size + client_size]

if not os.path.exists("./data"):
	os.mkdir("./data")

f = open('./data/server_set', 'w')
for item in server_set:
	f.write(str(item) + '\n')
f.close()

g = open('./data/client_set', 'w')
for item in client_set:
	g.write(str(item) + '\n')
g.close()		

h = open('./data/intersection', 'w')
for item in intersection:
	h.write(str(item) + '\n')
h.close()