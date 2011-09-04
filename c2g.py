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

# filter by embassy
me = ['ABUDHABI','ADANA','ADDISABABA','ADEN','ALEXANDRIA','ALGIERS','AMMAN','ANAKARA','ANAKRA','ANDOCTOBER','ANK','ANKARA','ANTANANARIVO','ASHGABAT','ASMARA','ASTANA','ATHENS','BAGHDAD','BAKU','BEIJING','BEIRUT','BERLIN','BERN','BONN','BRASILIA','BRUSSELS','BRUSSELSBE','BUCHAREST','CAIRO','CDRUSAREUR','COGARDTRACENYORKTOWN','COPENHAGEN','DAM','DAMASCUS','DHAHRAN','DJIBOUTI','DMS','DOHA','DTG','DUBAI','EFTOANKARA','EFTOCAIRO','EFTODAMASCUS','EFTOSANAA','FBIS','FBISGMP','FBISIAP','FRANKFURT','GAIN','GENEVA','GMP','HANOI','HELSINKI','IAP','IIR','IRANRPODUBAI','ISLAMABAD','ISTANBUL','IZMIR','JAKARTA','JEDDAH','JERUSALEM','KABUL','KAMPALA','KHARTOUM','KIRKUK','KUWAIT','KYIV','LONDON','LUXEMBOURG','MADRID','MANAMA','MONROVIA','MOSCOW','MOSUL','MUSCAT','NAIROBI','NDJAMENA','NEWDELHI','NICOSIA','NOUAKCHOTT','PARIS','RABAT','REFA','REOKIRKUK','RIYADH','ROME','RUEKJCS','SABOEMAILDATED','SANAA','SECDEF','SECSTATE','SECTION','SECTO','SEPTEMBER','SINGAPORE','SKOPJE','SOFIA','STATE','STOCKHOLM','TASHKENT','TBILISI','TELAVIV','THEHAGUE','THESSALONIKI','TIRANA','TOKYO','TOSEC','TREASURYDTG','TRIPOLI','TUNIS','UNVIE','UNVIEVIENNA','USCUSTOMS','USDAOANKARA','USDAOSANAADTG','USDOC','USEUBRUSSELS','USMISSIONGENEVA','USNATO','USUN','USUNNEWYORK','VATICAN','VIENNA','YEREVAN','ZAUG','ZFEB','ZJUL','ZNOV','ZOCT','ZSEP']

sg = g.subgraph(g.vs.select(_degree_gt=1, place_in=me))
print sg.summary()

# make clusters
i = 0
for c in sg.clusters():
    if len(c) > 5 and len(c) < 2000:
       i = i + 1
       ssg = sg.subgraph(g.vs.select(c))
       print ssg
       ssg.write_gml('middle-east-%d.gml' % i)

