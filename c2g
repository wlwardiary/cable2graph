#!/usr/bin/env python
#
# GPLv3 2011-2012 by anonymous
# 
# Create full graph from data/* input files 
#

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
g.vs['label'] = cable_ids
g.es['duration'] = duration
g.vs['place'] = place
g.vs['missing'] = missing
g.vs['timestamp'] = timestamp
g.vs['caption'] = caption
g.vs['classification'] = classification

g.vs['degree'] = g.degree()
g.vs['constraint'] = g.constraint()
g.vs['pagerank'] = g.pagerank()
g.vs['authority'] = g.authority_score()

g.write('full.graphml')
