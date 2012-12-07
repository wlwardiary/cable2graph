#!/usr/bin/env python
import igraph
from sys import argv, exit
from os import listdir, path
import re
from hashlib import md5
from collections import defaultdict

cable_ids = set()
missing_mrn = set()
embassy = set()
ref = []
timestamp_map = {}
missing_timestamps = {}
captions = {}
classifications = {}

print "Loading graph data..."
for i in open('data/embassy.list').readlines():
    embassy.add(i.strip().upper())

place_rgx = re.compile(r'^[0-9]{2}(' + '|'.join(embassy) + ')[0-9]+')

for i in open('data/all_ids.list').readlines():
    cable_ids.add(i.strip().upper())

for y in open('data/missing_mrn.list').readlines():
    missing_mrn.add(y.strip().upper())
    
for l in open('data/edges.list').readlines():
    ref.append((l.split(' ')[0].strip(),l.split(' ')[1].strip()))

for l in open('data/captions.list').readlines():
    cap_mrn, cap = l.split(' ')
    captions.update({ cap_mrn.strip(): cap.strip() })

for l in open('data/classifications.list').readlines():
    clss_mrn, clss= l.split(' ', 1) # only split first
    classifications.update({ clss_mrn.strip(): clss.strip() })

for j in open('data/dates.list').readlines():
    tmp_cable_id, tmp_ts = j.split(' ')
    timestamp_map.update({ tmp_cable_id.strip(): tmp_ts.strip() })

for dml in open('data/dates_missing.list').readlines():
    tmp_mrn, tmp_ts = dml.split(' ')
    missing_timestamps.update({ tmp_mrn.strip(): tmp_ts.strip() })

tags = defaultdict(list)

for k,v in [ (l.split() ) for l in open('data/tags_edges.list').readlines() ]:
    tags[k].append(v)

cable_ids = sorted(cable_ids)
ref = sorted(ref)

place = []
missing = []
timestamp = []
missing_timestamp = []
caption = []
classification = []

for c in cable_ids:
    m = re.search(place_rgx,c)
    if m is not None:
        place.append(m.group(1).upper())
    else:
        place.append('unknown')

    if c in missing_mrn:
        missing.append(1)
    else:
        missing.append(0)

    if c in timestamp_map:
        timestamp.append(int(timestamp_map[c]))
    elif c in missing_timestamps:
        timestamp.append(int(missing_timestamps[c]))
    else:
        timestamp.append(0)

    if c in captions:
        caption.append(captions[c])
    else:
        caption.append('')

    if c in classifications:
        classification.append(classifications[c])
    else:
        classification.append('')

# create dictionary with ids for every cable
cl = dict( [ (v,i) for i,v in enumerate(cable_ids) ] )
edges = [ (cl[f], cl[t]) for f, t in ref ]

# cal time duration between two verticies
id_cable_map = dict( [ (i,v) for i,v in enumerate(cable_ids) ] )
duration = []
for a,b in edges:
    acid = id_cable_map[a]
    bcid = id_cable_map[b]
    if acid not in missing_mrn and acid in timestamp_map:
        ts_a = int(timestamp_map[acid])
    else:
        ts_a = None

    if bcid not in missing_mrn and bcid in timestamp_map:
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

print 'Loading graph...'
g = igraph.Graph(edges, directed=False)
g.es['duration'] = duration
g.vs['label'] = cable_ids
g.vs['place'] = place
g.vs['missing'] = missing
g.vs['timestamp'] = timestamp
g.vs['caption'] = caption
g.vs['classification'] = classification

g.vs['degree'] = g.degree()
g.vs['constraint'] = g.constraint()
g.vs['pagerank'] = g.pagerank()
g.vs['authority'] = g.authority_score()

# make clusters
print "clusters"

# function to detect a star graph
def is_star(gstar):
    if gstar.girth() != 0:
        return False

    if gstar.diameter() != 2:
        return False
    
    if gstar.radius() != 1.0:
        return False

    # example [1, 1, 1, 1, 1, 1, 1, 11, 1, 1, 1, 1]
    dgr = gstar.degree()

    # all but one are 1
    if dgr.count(1) != (len(dgr) - 1):
        return False

    # the largest only exists once
    if dgr.count(max(dgr)) != 1:
        return False

    # value of the max is equal to amount of 1
    if max(dgr) != dgr.count(1):
        return False

    # yep, pretty sure it's a star
    return True

def walk(sg, visited, node):
    visited.append(node)
    # find possible new nodes to visit next
    next_nodes = [ (v['betweenness'], v.index) for v in sg.vs[node].neighbors() if v['betweenness'] > 0 and v.index not in visited ]
    if len(next_nodes) > 0:
        # take the node with the max betweenness
        btwn, n = max(next_nodes)
        print node, n, btwn, sg.vs[node]['label'], sg.vs[n]['label']
        # play it again sam
        walk(sg, visited, n)
    else:
        print "end."

def get_trail(sg):
    # list of visited nodes
    trail = []
    # get the edge with the max betweenness
    max_btwn = max(sg.es['betweenness'])
    top_edge = sg.es.select(betweenness_eq=max_btwn)
    for e in top_edge:
        # make sure the first run dosn't go into the direction of the source
        trail.append(e.source)
        # walk along both sides of the edge
        walk(sg, trail, e.target)
        walk(sg, trail, e.source)
    
    return trail

def get_tags(labels):
    tmp_tags = set()
    for label in labels:
        if label in tags:
            for tag in tags[label]:
                tmp_tags.add(tag)

    return tmp_tags

def save(sg, prefix):
    # create a uniq id for the graph
    # concat all sorted(!) label names and hash it
    idconcat = ''.join(sorted(sg.vs.get_attribute_values('label')))
    digest = md5(idconcat).hexdigest()
    di = sg.diameter()
    de = sg.density()
    ra = sg.radius()
    pl = sg.average_path_length()
    sg['diameter'] = di
    sg['density'] = de
    sg['radius'] = ra
    sg['avg_path_length'] = pl
    sg['tags'] = ','.join(get_tags(sg.vs['label']))
    filename = '%s_di%s_de%s_ra%s_pl%s_%s.graphml' % (prefix, di, de, ra, pl ,digest)
    print prefix, di, de, ra, pl
    print sg
    sg.write_graphml(filename)
    print filename, len(sg.es), len(sg.vs)

# use size of the largest cluster as limit
giant_size = g.clusters().giant().vcount()

# this is faster then calling len(cluster) in the for loop
cluster_sizes = g.clusters().sizes()

# also adds the cluster index
filterd_clusters = filter(
    lambda c: c[1] > 42 and c[1] < giant_size, 
    enumerate(cluster_sizes))

print "matched %s clusters" % len(filterd_clusters)
for cluster_index, cluster_size in filterd_clusters:
    # create the subgraph from the cluster index
    sg = g.clusters().subgraph(cluster_index)
    #sg.vs['degree'] = sg.degree()
    #sg.vs['constraint'] = sg.constraint()
    #sg.vs['pagerank'] = sg.pagerank()
    #sg.vs['authority'] = sg.authority_score()
    sg.vs['betweenness'] = sg.betweenness(directed=sg.is_directed())
    sg.es['betweenness'] = sg.edge_betweenness(directed=sg.is_directed())
    sg.vs['closeness'] = sg.closeness()
    sg.vs['eccentricity'] = sg.eccentricity()

    prefix = 'cluster_ci%s_cs%s' % (cluster_index, cluster_size)
    if is_star(sg):
        prefix = 'star'
    elif sg.density() < 0.01 and sg.average_path_length() > 5.0:
        trail = get_trail(sg)
        sg_trail = sg.vs.select(trail).subgraph()
        save(sg_trail, 'trail_ci%s' % cluster_index)

    save(sg, prefix)

# split the giant cluster into smaller communities
# new in igraph v0.6
print "loading giant"
giant = g.clusters().giant()

print "split giant cluster"
gcm = giant.community_multilevel()

prefix = 'community'
for sgcm in gcm.subgraphs():
    #sgcm.vs['degree'] = sgcm.degree()
    #sgcm.vs['constraint'] = sgcm.constraint()
    #sgcm.vs['pagerank'] = sgcm.pagerank()
    #sgcm.vs['authority'] = sgcm.authority_score()
    sgcm.vs['betweenness'] = sgcm.betweenness(directed=sgcm.is_directed())
    sgcm.es['betweenness'] = sgcm.edge_betweenness(directed=sgcm.is_directed())
    sgcm.vs['closeness'] = sgcm.closeness()
    sgcm.vs['eccentricity'] = sgcm.eccentricity()
    if sgcm.density() < 0.01 and sgcm.average_path_length() > 5.0:
        trail = get_trail(sgcm)
        sg_trail = sgcm.vs.select(trail).subgraph()
        save(sg_trail, 'community_trail')

    save(sgcm, prefix)

