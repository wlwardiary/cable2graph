#!/usr/bin/env python
import igraph, math, csv
from sys import argv, exit
from os import listdir, path
from jinja2 import Template, Environment, FileSystemLoader

CURDIR = path.dirname(path.abspath(__file__))
env = Environment(loader=FileSystemLoader(CURDIR))
svg_tmpl = env.get_template('svg.tmpl')

g = igraph.load(argv[1])

# load ReVerb sentences result .tsv
# http://reverb.cs.washington.edu/

reverb_csv = csv.reader(
        open(CURDIR + '/middle-east.reverb'), 
        delimiter='\t', 
        quotechar = None,
        lineterminator = '\n')

reverb_map = {}
for row in reverb_csv:
    type, reverb_cable_id, num, argument1, relation, argument2, score = row
    if float(score) > 0.7:
        if reverb_map.has_key(reverb_cable_id):
            reverb_map[reverb_cable_id].append({
                    'a1': argument1, 
                    'rel': relation,
                    'a2': argument2,
                    'score': score
                    })
        else:
            reverb_map[reverb_cable_id] = [{ 
                    'a1': argument1, 
                    'rel': relation,
                    'a2': argument2,
                    'score': score
                    }]

sentence = []
for l in g.vs.get_attribute_values('label'):
    if l in reverb_map.keys():
        sentence.append(reverb_map[l])
    else:
        sentence.append('')

g.vs['sentence'] = sentence

# add uri to graph
cmap = {}
f = open(CURDIR + '/all.map')
for l in f.readlines():
    k,v = l.strip().split()
    cmap[k.strip()] = v.strip()

uri = []

for l in g.vs.get_attribute_values('label'):
    if l in cmap:
        uri.append('http://wikileaks.org/%s' % cmap[l])
    else:
        uri.append('')

g.vs['uri'] = uri

layout = g.layout('fr')

width = len(g.vs) * 20
height = len(g.vs) * 20

w = '%d' % width
h = '%d' % height

xw = '%.4f' % (width/2.0)
xh = '%.4f' % (height/2.0)

labels = g.vs.get_attribute_values('label')
colors = g.vs.get_attribute_values('color')
uris = g.vs.get_attribute_values('uri')
sentences = g.vs.get_attribute_values('sentence')
vertex_size = 10

# from igraph.Graph.write_svg

maxs=[layout[0][dim] for dim in range(2)]
mins=[layout[0][dim] for dim in range(2)]
        
for rowidx in range(1, len(layout)):
    row = layout[rowidx]
    for dim in range(0, 2):
        if maxs[dim]<row[dim]: maxs[dim]=row[dim]
        if mins[dim]>row[dim]: mins[dim]=row[dim]
        
sizes=[width-2*vertex_size, height-2*vertex_size]
halfsizes=[(maxs[dim]+mins[dim])/2.0 for dim in range(2)]
ratios=[sizes[dim]/(maxs[dim]-mins[dim]) for dim in range(2)]
layout=[[(row[0]-halfsizes[0])*ratios[0], \
         (row[1]-halfsizes[1])*ratios[1]] \
        for row in layout]

edges = []
vertices = []

for eidx, edge in enumerate(g.es):
    vidxs = edge.tuple
    x1 = layout[vidxs[0]][0]
    y1 = layout[vidxs[0]][1]
    x2 = layout[vidxs[1]][0]
    y2 = layout[vidxs[1]][1]
    angle = math.atan2(y2-y1, x2-x1)
    x2 = x2 - vertex_size*math.cos(angle)
    y2 = y2 - vertex_size*math.sin(angle)
    edges.append(
        {'x1': '%.4f' % x1, 
         'y1': '%.4f' % y1, 
         'x2': '%.4f' % x2, 
         'y2': '%.4f' % y2 })

for vidx in range(g.vcount()):
    vertices.append( { 
        'x': '%.4f' % layout[vidx][0], 
        'y': '%.4f' % layout[vidx][1],
        'label': str(labels[vidx]),
        'uri': str(uris[vidx]),
        'sentences': sentences[vidx],
        'class': str(colors[vidx]) 
        } )

print svg_tmpl.render(
    height = h,
    width = w,
    xh = xh,
    xw = xw,
    edges = edges, 
    vertices = vertices)

