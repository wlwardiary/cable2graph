#!/usr/bin/env python
import igraph
import cPickle as pickle
from sys import argv, exit
from os import listdir, path
import re

p = re.compile(r'[A-Z]+')

cable_ids = set()
missing = set()
ref = []

for i in open('all_ids.list').readlines():
    cable_ids.add(i.strip())

for y in open('diff_ids.list').readlines():
    missing.add(y.strip())
    
for l in open('edges.list').readlines():
    ref.append((l.split(' ')[0].strip(),l.split(' ')[1].strip()))

cable_ids = sorted(cable_ids)
ref = sorted(ref)

place = []
color = []
for c in cable_ids:
    m = re.search(p,c)
    if m is not None:
        place.append(m.group(0))
    else:
        place.append(None)
    if c in missing:
        color.append('red')
    else:
        color.append(None)

print len(cable_ids)
print len(ref)

if path.exists('calccache'):
    print 'Loading calc cache...'
    edges, weight = pickle.load(open('calccache'))
else:
    print "ids"
    # create dictionary with ids for every cable
    cl = dict( [ (v,i) for i,v in enumerate(cable_ids) ] )

    print "edges"
    # create numeric egdes from the cable "refernce" mapping
    edges = [ (cl[f], cl[t]) for f, t in ref ]

    print "count"
    # count the weight
    ew = [ [e, edges.count(e)] for e in set(edges) ]

    print "split"
    # split edge and weight
    edges, weight = map(list, zip(*ew))

    print "Saving calc cache..."
    pickle.dump( (edges, weight), open('calccache','w'))


print "graph"
if path.exists('graphcache'):
    print 'Loading graph cache...'
    g = pickle.load(open('graphcache'))
else:
    # load numeric edges into graph
    g = igraph.Graph(edges)
    g.es['weight'] = weight
    g.vs['label'] = cable_ids
    g.vs['place'] = place
    g.vs['color'] = color
    g.vs['degree'] = g.degree()
    g.vs['constraint'] = g.constraint(weights='weight')
    print 'Saving graph cache.'
    pickle.dump( g, open('graphcache','w'))

print "all fine, read the source"
exit()

# write the full big fkn graph
# g.write_gml('full.gml')
# exit()

# filter by embassy
# de = ['BERLIN','BONN','DUESSELDORF','DUSSELDORF','FRANKFURT','HAMBURG','LEIPZIG','MUNICH','STUTTGART']
# sg = g.subgraph(g.vs.select(_degree_gt=2, place_in=de))
# print sg.summary()
# sg.write_gml('de.gml')
# exit()

# make clusters
# i = 0
# for c in g.clusters():
#     if len(c) > 50:
#        i = i + 1
#        sg = g.subgraph(g.vs.select(c))
#        print sg
#        sg.write_gml('aa%s.gml' % i)
#
# exit()

