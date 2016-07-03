import os
import operator
import networkx as nx
import matplotlib.pyplot as plt
from networkx.drawing.nx_agraph import graphviz_layout
import mpld3

#maps out the directory into a set of tuples representing edges
#function returns the set of edges as well as dictionary of node weights for files
#where the weight for each file (not folders) is its size in bytes
def returnEdgeList(rootDir):
	edgePath = []
	dictionary = {}
	
	#map out all the files first
	files = [f for f in os.listdir(rootDir) if os.path.isfile(os.path.join(rootDir, f))]
	for fname in files:
		edgePath.append((rootDir,rootDir+'/'+fname))
		dictionary[rootDir+'/'+fname]=os.path.getsize(rootDir+'/'+fname)

	#map out all folders and then recurse into them
	for subdir in next(os.walk(rootDir))[1]:
		edgePath.append((rootDir,rootDir+'/'+subdir))
		results = returnEdgeList(rootDir+'/'+subdir)
		edgePath = edgePath + results[0]
		dictionary.update(results[1])
	return [edgePath, dictionary]


#normalizes the dictionary so that everything is proportional to the largest
#value in the dictionary
def normalizeDictionary(dictionary):
	maximum=dictionary[max(dictionary.iteritems(), key=operator.itemgetter(1))[0]]
	for key, value in dictionary.iteritems():
		dictionary[key] = int(float(value)/float(maximum)*10000)
	return dictionary




results = returnEdgeList('.');

G = nx.Graph()
G.add_edges_from(results[0])

#for node color
val_map = {1: 10}
values = [val_map.get(node, 0.25) for node in G.nodes()]

#for node size
val_z={'.':100}
val_z.update(results[1])
val_z = normalizeDictionary(val_z)
val_z['.']=100;
vals = [val_z.get(node, 0.25) for node in G.nodes() ]

pos = graphviz_layout(G, prog="twopi", root='.')
fig, ax = plt.subplots()
nx.draw(G,pos,node_color=values,node_size=vals,with_labels=False,alpha=0.5)

#labeling of node names enabled
scatter = nx.draw_networkx_nodes(G, pos,node_size=30)
labels = G.nodes()
tooltip = mpld3.plugins.PointLabelTooltip(scatter, labels=labels)
mpld3.plugins.connect(fig, tooltip)

mpld3.show()
