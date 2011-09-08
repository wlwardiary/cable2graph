#!/usr/bin/env python
import csv, re, sys, os.path

if len(sys.argv) < 3: 
    print "Usage: %s cables.csv ID1 [ID2 ID3]" % sys.argv[0]
    sys.exit()

sys.argv.pop(0)
source = sys.argv.pop(0)
search_cables = sys.argv

csv.field_size_limit(131072*2)

try:
    content = csv.reader(open(source), delimiter=',', quotechar='"', escapechar='\\')
except IOError:
    sys.stderr.write("Error: could not open source %s\n" % source)
    sys.exit(1)


for row in content:
    line_num, cabledate, cable, location, classification, referrer, header, body = row

    if cable.strip() in search_cables:
        search_cables.remove(cable.strip())
        header_filename = 'header_%s.txt' % cable.strip()
        body_filename = 'body_%s.txt' % cable.strip()
        h = open(header_filename, 'w')
        h.write(header)
        h.close()
        b = open(body_filename, 'w')
        b.write(body)
        b.close()

    if len(search_cables) == 0:
        sys.exit()
