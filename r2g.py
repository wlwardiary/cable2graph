#!/usr/bin/env python
# from -> to routings as graph
# GPLv3 by anonymous 2012

import igraph

print "Loading edges..."
l = [ (l.split('\t')) for l in open('data/from_to.list').readlines() ]

# make a set of all routing indicators
ri = set()
[ (ri.add(f.strip()),ri.add(t.strip())) for mrn,f,t in l ]

# give every routing indicator a number and map it into a dict
rimap = dict()
[ rimap.update({r: num}) for num, r in enumerate(sorted(ri)) ]

# edge list
ft = [ (rimap[f.strip()], rimap[t.strip()]) for mrn, f, t in l ]

print "All edges before weight count: %s" % len(ft)
# count the edges
try:
    from collections import Counter
    ftcnt = Counter(ft)
    edges, weight = map(list, zip(*ftcnt.iteritems()))
except ImportError:
    print "WARN: use python >= 2.7 for faster weight counting"
    ftcnt = [ (t, ft.count(t)) for t in set(ft) ]
    edges, weight = map(list, zip(*ftcnt))

g = igraph.Graph(edges, directed=True)
g.es['weight'] = weight
g.vs['label'] = sorted(ri)

print g.summary()
print "Writing from_to.gml..."
g.write_gml('from_to.gml')

