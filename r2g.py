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
g.vs['label'] = sorted(ri)

g.es['weight'] = weight
g.es['betweenness'] = g.es.edge_betweenness()
g.vs['authority'] = g.authority_score(weights='weight')
g.vs['in-coreness'] = g.coreness(mode='IN')
g.vs['out-coreness'] = g.coreness(mode='OUT')
g.vs['convergence-degree'] = g.convergence_degree()
g.vs['degree'] = g.degree()
g.vs['in-degree'] = g.indegree()
g.vs['out-degree'] = g.outdegree()
g.vs['weighted-degree'] = g.strength(weights='weight')
g.vs['weighted-in-degree'] = g.strength(mode='IN', weights='weight')
g.vs['weighted-out-degree'] = g.strength(mode='OUT', weights='weight')

print g.summary()
print "Writing from_to.gml..."
g.write_gml('from_to.gml')

