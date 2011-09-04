#!/usr/bin/env python
import igraph, math
from sys import argv, exit
from os import listdir, path
from jinja2 import Template, Environment, FileSystemLoader

CURDIR = path.dirname(path.abspath(__file__))
env = Environment(loader=FileSystemLoader(CURDIR))
svg_tmpl = env.get_template('svg.tmpl')

g = igraph.load(argv[1])

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

width = 960
height = 800

w = '%d' % width
h = '%d' % height

xw = '%.4f' % (width/2.0)
xh = '%.4f' % (height/2.0)

labels = g.vs.get_attribute_values('label')
colors = g.vs.get_attribute_values('color')
uris = g.vs.get_attribute_values('uri')
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
        'class': str(colors[vidx]) 
        } )

print svg_tmpl.render(
    height = h,
    width = w,
    xh = xh,
    xw = xw,
    edges = edges, 
    vertices = vertices)

