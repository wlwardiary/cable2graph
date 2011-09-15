#!/usr/bin/env python
import igraph, math, csv
from sys import argv, exit
from os import listdir, path
from jinja2 import Template, Environment, FileSystemLoader
from optparse import OptionParser
from datetime import datetime

parser = OptionParser()
parser.add_option("-t", "--tmpl", dest="template",
    default="svg.tmpl",
    help="Jinja html/svg template NAME. Default: svg.tmpl", 
    metavar="NAME")

parser.add_option("-g", "--gml", dest="gmlfile",
    help="Single source graph in gml format FILE", metavar="FILE")

parser.add_option("-l", "--load-from", dest="gmllist",
    help="Load all .gml graphs listed in FILE", metavar="FILE")

parser.add_option("-d", "--dest", dest="destdir",
    default=".",
    help="Destination DIR. Default: current dir", 
    metavar="DIR")

parser.add_option("-r", "--reverb", dest="reverb",
    help="Load sentences from a ReVerb result tsv FILE (e.g. mycables.reverb)", metavar="FILE")

parser.add_option("-s", "--subjects", dest="subjects",
    default="subjects.list",
    help="Load map of label -> subject. Default: subjects.list", metavar="FILE")

parser.add_option("-u", "--uri", dest="uri",
    default="all.map",
    help="Load map of label -> uri from FILE. Default: all.map", metavar="FILE")
(options, args) = parser.parse_args()

graph_files = set()
if options.gmlfile:
    graph_files.add(options.gmlfile.strip())

if options.gmllist:
    gfh = open(options.gmllist)
    for gf in gfh.readlines():
        graph_files.add(gf.strip())

if len(graph_files) < 1:
    print "No source .gml files"
    exit(1)

def format_timestamp(ts, format = '%Y-%m-%d'):
    d = datetime.fromtimestamp(float(ts))
    return d.strftime(format)

CURDIR = path.dirname(path.abspath(__file__))
env = Environment(loader=FileSystemLoader(CURDIR))
env.filters['formatts'] = format_timestamp
svg_tmpl = env.get_template(options.template)

# load optional ReVerb sentences result .tsv
# http://reverb.cs.washington.edu/

if options.reverb:
    reverb_csv = csv.reader(
            open(options.reverb), 
            delimiter='\t', 
            quotechar = None,
            lineterminator = '\n')

    reverb_map = {}
    for row in reverb_csv:
        type, reverb_cable_id, num, argument1, relation, argument2, score = row
        # TODO have a custom threshold as cmd line parameter
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

# load optional uri map
if options.uri:
    cmap = {}
    f = open(options.uri)
    for l in f.readlines():
        k,v = l.strip().split()
        cmap[k.strip()] = v.strip()


# load optional subject map
if options.subjects:
    smap = {}
    f = open(options.subjects)
    for l in f.readlines():
        k,v = l.split(' ',1)
        smap[k.strip()] = v.strip()

for gml in graph_files:
    destfile = "%s/%s.html" % (options.destdir, path.basename(gml))
    if path.exists(destfile):
        print  "%s exists. skipping" % destfile
        continue

    # load graph from file
    g = igraph.load(gml)

    # apply sentences to graph
    if options.reverb:
        sentence = []
        for l in g.vs.get_attribute_values('label'):
            if l in reverb_map.keys():
                sentence.append(reverb_map[l])
            else:
                sentence.append('')

        g.vs['sentence'] = sentence

    # apply uris to graph
    if options.uri:
        uri = []
        for l in g.vs.get_attribute_values('label'):
            if l in cmap:
                # TODO move into uri file
                uri.append('http://wikileaks.org/%s' % cmap[l])
            else:
                uri.append('')

        g.vs['uri'] = uri

    # apply subjects to graph
    if options.subjects:
        subjects = []
        for l in g.vs.get_attribute_values('label'):
            if l in smap:
                subjects.append(smap[l])
            else:
                subjects.append('(no subject)')

        g.vs['subjects'] = subjects

    # create x,y positions
    layout = g.layout_fruchterman_reingold(weights='weight', maxiter=3000)

    # calc graph size based on number of vertices
    width = len(g.vs) * 20
    height = len(g.vs) * 20
    
    if width < 800: 
        width = 800
    if height < 600: 
        height = 600

    w = '%d' % (width+400)
    h = '%d' % (height+300)

    xw = '%.4f' % ((width+400)/2.0)
    xh = '%.4f' % ((height+300)/2.0)

    labels = g.vs.get_attribute_values('label')
    colors = g.vs.get_attribute_values('color')
    degrees = g.vs.get_attribute_values('degree')
    timestamps = g.vs.get_attribute_values('timestamp')

    if options.uri:
        uris = g.vs.get_attribute_values('uri')
    if options.subjects:
        subjects = g.vs.get_attribute_values('subjects')
    if options.reverb:
        sentences = g.vs.get_attribute_values('sentence')

    # from igraph.Graph.write_svg
    vertex_size = 10

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
        tmpd = {
            'x': '%.4f' % layout[vidx][0], 
            'y': '%.4f' % layout[vidx][1],
            'label': str(labels[vidx]),
            'degree': str(int(degrees[vidx])),
            'timestamp': str(timestamps[vidx]),
            'class': str(colors[vidx]) 
        }
        # optional
        if options.uri:
            tmpd.update({'uri': str(uris[vidx])})
        if options.subjects:
            tmpd.update({'subject': str(subjects[vidx])})

        if options.reverb:
            tmpd.update({'sentences': sentences[vidx]})

        vertices.append(tmpd)

    dfh = open(destfile,'w')
    dfh.write(svg_tmpl.render(
        height = h,
        width = w,
        xh = xh,
        xw = xw,
        edges = edges, 
        vertices = vertices))
    print "%s -> %s" % (gml, destfile)

# GPLv3 anonymous
