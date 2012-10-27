#!/usr/bin/env python
import igraph
import cPickle as pickle
from sys import argv, exit
from os import listdir, path
import re
from hashlib import md5

cable_ids = set()
missing = set()
embassy = set()
ref = []
timestamp_map = {}

print "Loading graph data..."
for i in open('data/embassy.list').readlines():
    embassy.add(i.strip().upper())

place_rgx = re.compile(r'^[0-9]{2}(' + '|'.join(embassy) + ')[0-9]+')

for i in open('data/all_ids.list').readlines():
    cable_ids.add(i.strip().upper())

for y in open('data/diff_ids.list').readlines():
    missing.add(y.strip().upper())
    
for l in open('data/edges.list').readlines():
    ref.append((l.split(' ')[0].strip(),l.split(' ')[1].strip()))

for j in open('data/dates.list').readlines():
    tmp_cable_id = j.split(' ')[0].strip()
    tmp_ts = j.split(' ')[1].strip()
    timestamp_map.update({tmp_cable_id: tmp_ts})

cable_ids = sorted(cable_ids)
ref = sorted(ref)

place = []
color = []
timestamp = []
for c in cable_ids:
    m = re.search(place_rgx,c)
    if m is not None:
        place.append(m.group(1).upper())
    else:
        place.append('unknown')
    if c in missing:
        color.append('red')
    else:
        color.append('black')
    if timestamp_map.has_key(c):
        timestamp.append(int(timestamp_map[c]))
    else:
        timestamp.append(0)

# create dictionary with ids for every cable
cl = dict( [ (v,i) for i,v in enumerate(cable_ids) ] )
edges = [ (cl[f], cl[t]) for f, t in ref ]

# cal time duration between two verticies
id_cable_map = dict( [ (i,v) for i,v in enumerate(cable_ids) ] )
duration = []
for a,b in edges:
    acid = id_cable_map[a]
    bcid = id_cable_map[b]
    if acid not in missing:
        ts_a = int(timestamp_map[acid])
    else:
        ts_a = None

    if bcid not in missing:
        ts_b = int(timestamp_map[bcid])
    else:
        ts_b = None

    if ts_a is None or ts_b is None:
        dur = 0
    elif ts_a > ts_b:
        dur = ts_a - ts_b
    elif ts_b > ts_a:
        dur = ts_b - ts_a
    duration.append(int(dur))

if path.exists('graphcache'):
    print 'Loading graph cache...'
    g = pickle.load(open('graphcache'))
else:
    # load numeric edges into graph
    print 'Loading graph...'
    g = igraph.Graph(edges)
    g.to_directed()
    g.es['duration'] = duration
    g.vs['label'] = cable_ids
    g.vs['place'] = place
    g.vs['color'] = color
    g.vs['timestamp'] = timestamp
    print "calculating..."
    print "..degree"
    g.vs['degree'] = g.degree()
    print "..constraint"
    g.vs['constraint'] = g.constraint()
    print "..page rank"
    g.vs['pagerank'] = g.pagerank()
    print "..authority"
    g.vs['authority'] = g.authority_score()
    print 'Saving graph cache.'
#    print "..betweenness"
#    g.vs['betweenness'] = g.betweenness(directed=g.is_directed())
#    g.es['betweenness'] = g.edge_betweenness(directed=g.is_directed())
#    print "..closeness"
#    g.vs['closeness'] = g.closeness()
#    print "..eccentricity"
#    g.vs['eccentricity'] = g.eccentricity()
    pickle.dump( g, open('graphcache','w'))

print "all fine, read the source"
exit()

# write the full big fkn graph
# g.write_gml('full.gml')
# exit()

# filter by embassy
#de = ['BERLIN']
#sg = g.subgraph(g.vs.select(_degree_gt=2, place_in=de))
#print sg.summary()
#sg.write_gml('de.gml')
#exit()

# make clusters
print "clusters"
# use size of the largest cluster as limit
giant_size = len(g.clusters().giant().vs)

# this is faster then calling len(cluster) in the for loop
cluster_sizes = g.clusters().sizes()

# also adds the cluster index
filterd_clusters = filter(
    lambda c: c[1] > 10 and c[1] < giant_size, 
    enumerate(cluster_sizes))

print "matched %s clusters" % len(filterd_clusters)
for cluster_index, cluster_size in filterd_clusters:
    # create the subgraph from the cluster index
    sg = g.clusters().subgraph(cluster_index)
    sg.to_directed()
    sg.vs['betweenness'] = sg.betweenness(directed=sg.is_directed())
    sg.es['betweenness'] = sg.edge_betweenness(directed=sg.is_directed())
    sg.vs['closeness'] = sg.closeness()
    sg.vs['eccentricity'] = sg.eccentricity()
    # create a uniq id for the graph
    # concat all sorted(!) label names and hash it
    idconcat = ''.join(sorted(sg.vs.get_attribute_values('label')))
    filename = md5(idconcat).hexdigest()
    sg.write_gml('%s.gml' % filename)
    print filename, len(sg.es), len(sg.vs)

# split the giant cluster into smaller communities
# new in igraph v0.6

print "split giant cluster"
g.to_undirected()
gcm = g.clusters().giant().community_multilevel()
for sgcm in gcm.subgraphs():
    sgcm.to_directed()
    sgcm.vs['betweenness'] = sgcm.betweenness(directed=sgcm.is_directed())
    sgcm.es['betweenness'] = sgcm.edge_betweenness(directed=sgcm.is_directed())
    sgcm.vs['closeness'] = sgcm.closeness()
    sgcm.vs['eccentricity'] = sgcm.eccentricity()
    idconcat = ''.join(sorted(sgcm.vs.get_attribute_values('label')))
    filename = md5(idconcat).hexdigest()
    sgcm.write_gml('%s.gml' % filename)
    print filename, len(sgcm.es), len(sgcm.vs)

