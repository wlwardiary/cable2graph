#!/usr/bin/env python
# TAGS to graph
# GPLv3
import igraph
from itertools import repeat

# load MRNs and TAGS
mrns = sorted([ l.strip() for l in open('data/cable_ids.list').readlines() ])
subject_tags = sorted([ l.strip() for l in open('data/tags.subject').readlines() ])
program_tags = sorted([ l.strip() for l in open('data/tags.program').readlines() ])
tags_edges = [ (l.split()) for l in open('data/tags_edges.list').readlines() ]

# merge everything together
everything = []
everything.extend(mrns)
everything.extend(subject_tags)
everything.extend(program_tags)

# give everything numeric ids and map it
all_id = dict( [ (v,i) for i,v in enumerate(everything) ] )
num_edges = [ (all_id[f], all_id[t]) for f, t in tags_edges ]

# create a node type map. 1 node type A, 0 node type B
t1 = [ f for f in repeat(1, len(mrns)) ]
t2 = [ f for f in repeat(0, len(subject_tags)) ]
t3 = [ f for f in repeat(0, len(program_tags)) ]

types = []
types.extend(t1)
types.extend(t2)
types.extend(t3)

# create the graph with two node types
bpg = igraph.Graph.Bipartite(types, num_edges)
bpg.vs['label'] = everything 
bpg.vs['degree'] = bpg.vs.degree()
print bpg.summary()

# get the largest cluster
giant = bpg.clusters().giant()

# detect communities
cm = giant.community_multilevel()
        
# list TAGS often mentioned together
for c in cm.subgraphs():
    print c.summary()
    v = c.vs.select(type_eq=0, degree_gt=max(c.vs['degree'])/10)
    print v.get_attribute_values('label'), v.get_attribute_values('degree') 

