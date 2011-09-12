#!/usr/bin/env python
import csv, re, sys, os.path, time
from datetime import datetime

limit = None
if len(sys.argv) == 3:
    limit = int(sys.argv[2])

source = sys.argv[1]

# remove page break from body to avoid problems 
# when subject is spaning multiple pages

re_page = re.compile(r'^(\ {1,30}(CONFIDENTIAL|UNCLASSIFIED)\s+){1,3}^PAGE\s+[0-9]{2}.*\n', re.M)

re_ref = re.compile(r'^REF: (.*)$', re.M)
re_cable_id = re.compile(r'\W+[A-Z]\W+([0-9]{2,4})?([a-zA-Z\s]{3,12})\s([0-9]{1,8})')
re_subject = re.compile(r'^(SUBJ|SUBJECT):([\s\S]*?)(?=(?:\n\s\n)|(?:CLASSIFIED BY|Classified by|REF:|REFS:))', re.M)

csv.field_size_limit(131072*2)

try:
    content = csv.reader(open(source), delimiter=',', quotechar='"', escapechar='\\')
except IOError:
    sys.stderr.write("Error: could not open source %s\n" % source)
    sys.exit(1)

count = 0

cable_ids = set()
ref_ids = set()
ref_cnt = {}
diff_cnt = {}
edges = []
dates = {}
subjects = {}

for row in content:
    count = count + 1
    if limit is not None and count > limit:
        print "Limit %d reached." % limit
        sys.exit(0)

    # read csv values
    line_num, cabledate, cable, location, classification, referrer, head, body = row

    tdate = datetime.strptime(cabledate.strip(), '%m/%d/%Y %H:%M')
    timestamp = int(time.mktime(tdate.timetuple()))
    dates.update({cable:timestamp})

    cable_ids.add(cable)
    for r in referrer.split('|'):
        if len(r.strip()) > 0:
            edges.append((cable.upper(),r.upper()))
            ref_ids.add(r)
            if ref_cnt.has_key(r):
                ref_cnt[r] = ref_cnt[r] + 1
            else:
                ref_cnt[r] = 1


    # remove page break
    body_filterd, page_match_count = re.subn(re_page,'',body)

    subject_match = re.search(re_subject, body_filterd)
    if subject_match is not None:
        subject = subject_match.group(2).replace('\n','').strip()
    else:
        print cable
        subject = ''

    subjects.update({cable:subject})


#    re_referrer = re.search(re_ref, body)
#    if re_referrer is not None:
#        month, day, year = cabledate.split(' ')[0].split('/') # 3/9/1972 5:40
#        ref = re_referrer.group(0).strip()
#        re_cids = re.findall(re_cable_id, ref)
#        for (ref_year, ref_name, ref_id)  in re_cids:
#            if ref_year == '':
#                ref_year = year[2:4]
#            x = "%s%s%s" % (ref_year, ref_name.replace(' ','').upper(), ref_id)
#            ref_ids.add(x)

    if count % 10000 == 0:
        print count

print len(cable_ids)
print len(ref_ids)
print len(ref_cnt)
diff_ids = ref_ids.difference(cable_ids)
print len(diff_ids)
print len(dates)

for d in diff_ids:
    diff_cnt[d] = ref_cnt[d]

print len(diff_cnt)

cf = file('cable_ids.list','w')
rf = file('ref_ids.list','w')
df = file('diff_ids.list','w')
rcf = file('ref_cnt.list','w')
dcf = file('diff_cnt.list','w')
ef = file('edges.list','w')
datef = file('dates.list','w')
subf = file('subjects.list','w')

for i in sorted(cable_ids):
    cf.write('%s\n' % i)
cf.close()

for i in sorted(ref_ids):
    rf.write('%s\n' % i)
rf.close()

for i in sorted(diff_ids):
    df.write('%s\n' % i)
df.close()

for k,i in sorted(ref_cnt.iteritems()):
    rcf.write('%s %s\n' % (i,k))
rcf.close()

for k,i in sorted(diff_cnt.iteritems()):
    dcf.write('%s %s\n' % (i,k))
dcf.close()

for e in sorted(edges):
    ef.write('%s %s\n' % e)
ef.close()

for k,v in sorted(dates.iteritems()):
    datef.write('%s %s\n' % (k,v))
datef.close()

for k,v in sorted(subjects.iteritems()):
    subf.write('%s %s\n' % (k,v))
subf.close()
