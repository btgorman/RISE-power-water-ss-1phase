import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import math

rts_coords = pd.read_csv('ieee rts-79 coords.csv', header=1)
rts_branches = pd.read_csv('ieee rts-79 branches.csv', header=0)
rts_coords = rts_coords.values
rts_branches = rts_branches.values

dict_coords = {}
for row in rts_coords:
	temp_dict = {int(row[0]): (float(row[1]), float(row[2]))}
	dict_coords.update(temp_dict)

for branch in rts_branches:
	from_node = int(branch[1])
	to_node = int(branch[2])
	distance = 0.1 * float(branch[3])

	x1, y1 = dict_coords[from_node]
	x2, y2 = dict_coords[to_node]

	error_abs = distance - ((x1-x2)**2 + (y1-y2)**2)**0.5
	if distance == 0.:
		print('Branch {} has distance {} and ??? abs error of {}'.format(int(branch[0]), distance, error_abs))
	elif math.fabs(error_abs / distance) > 0.001:
		print('Branch {} has distance {} and HIGH error of {}%'.format(int(branch[0]), distance, error_abs*100./distance))
	else:
		pass
		# print('Branch {} has distance {} and LOW error of {}%'.format(int(branch[0]), distance, error_abs*100./distance))

# G = nx.Graph()

# G.add_node(1)
# G.add_node(2)
# G.add_node(3)

# G.add_edge(1,2, length=200)
# G.add_edge(1,3, length=300)
# G.add_edge(2,3, length=1000)

# posit = pos=nx.circular_layout(G)
# nx.draw(G, pos=posit)
# nx.draw_networkx_labels(G, pos=posit)
# nx.draw_networkx_edge_labels(G, pos=posit)

# plt.show()