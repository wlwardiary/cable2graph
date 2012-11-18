#!/usr/bin/env python
import csv, re, sys, os.path, time
from datetime import datetime

limit = None
if len(sys.argv) == 3:
    limit = int(sys.argv[2])

source = sys.argv[1]

# dirty data, be gentle

# remove page break from body to avoid problems 
# when subject is spaning multiple pages
re_page = re.compile(r'^(\ {1,30}(CONFIDENTIAL|SECRET|UNCLASSIFIED)\s+){1,3}^PAGE\s+[0-9]{2}.*\n', re.M)

# multi line reference from body
# second regex is matching mrn, see below
re_ref = re.compile(r'^(REF|REFS|Ref|RETELS|REFTEL):([\s\S]*?)(?=(?:\n\s\n)|1\.|SIPDIS|Summary|SUMMARY|Classified\ By|CLASSIFIED\ BY|Sensitive\ But\ Unclassified|SENSITIVE\ BUT\ UNCLASSIFIED)', re.M)

# parse TAGS over multiple lines with a couple of stop words
re_tags = re.compile(r'^TAGS:([\s\S]*?)(?=(?:\n\s\n)|(?:CLASSIFIED\ BY|Classified\ by|REF:|REFS:|Ref:|RETELS:|REFTEL:|REF\ :|SUBJECT:|Subject:|SUBJ:|Subj:|E\.O\.|\*\*\*\*|FINAL\ SECTION\ OF|SECRET\ |CONFIDENTIAL\ |UNCLASSIFIED\ |COMBINE:))', re.M)

# source cabletags website
all_subject_tags = [ l.strip() for l in open('data/tags.subject').readlines() ] 
all_program_tags = [ l.strip() for l in open('data/tags.program').readlines() ] 

re_subject_tags = re.compile(r'(' + '|'.join(all_subject_tags) + r')',re.M)
re_program_tags = re.compile(r'(' + '|'.join(all_program_tags) + r')',re.M)

# people mentioned in the TAGS field
re_ppl_tags = re.compile(r'(OVIP|OREP|SP|JO|HO|CO|RO|PINR|OTRA|PREL|APER|CASC|CLOK|CVIS|DR|EG|FR|MX|NI|PM|PA|SCE|SY|UN|US|USPTO|VM)(\W+)?\(.*\)')

# try to match a valid MRN
re_mrn1 = re.compile(r'\W+[A-Z]\W+([0-9]{2,4})?([a-zA-Z\s]{3,12})\s([0-9]{1,8})')
re_mrn2 = re.compile(r'([0-9]{2,4})?([a-zA-Z]{3,18})\s([0-9]{1,8})')
re_mrn3 = re.compile(r'\b([A-Z][\s\W]{1,3})?([0-9]{2,4})?\s?([a-zA-Z\s]{3,18})\s?([0-9]{1,8})\W')
re_mrn4 = re.compile(r'\b([A-Z][\s\W]{1,3})?([0-9]{2,4})?\s?([a-zA-Z\s]{3,18})\s?([0-9]{1,8})(\s+\(NOTAL|EXDIS|NODIS|Notal|Exdis|Nodis\))?\W')

# load embassy names
emb = [ l.strip() for l in open('data/embassy.list').readlines() ] 

# list like A. B. C. / A) B) C)
mrn5_list = r'([a-zA-Z][\s\W]{1,3})?'

# year as 0x 9x 20xx 19xx
mrn5_year = r'([0,6-9][0-9]|19[0-9]{2}|20[0-9]{2})?'
mrn5_num = r'([0-9]{1,10})'
# caption after the MRN like (NOTAL) or (EXDIS)
mrn5_caption = '(\s+\((NOTAL|EXDIS|NODIS|Notal|Exdis|Nodis)\))?'
re_mrn5 = re.compile(
    r'\W' + 
    mrn5_list + 
    mrn5_year + 
    r'(\s)?(' + '|'.join(emb) + r')(\s)?' + 
    mrn5_num + 
    mrn5_caption + 
    '\W'
    )

# find subject over multiple lines
re_subject = re.compile(r'^(SUBJ|SUBJECT):([\s\S]*?)(?=(?:\n\s\n)|(?:CLASSIFIED BY|Classified by|REF:|REFS:))', re.M)

csv.field_size_limit(131072*2)

try:
    content = csv.reader(open(source), delimiter=',', quotechar='"', escapechar='\\')
except IOError:
    sys.stderr.write("Error: could not open source %s\n" % source)
    sys.exit(1)

count = 0

mrns = set()

# reference from header
ref_ids = set()
ref_cnt = {}

# reference from body text via regex
ref_from_text = {}
ref_body_mrns = set()
ref_body_cnt = {}

diff_cnt = {}
edges = set()
dates = {}
subjects = {}
classifications = {}
locations = set()
tags = {}
tag_edges = set()

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
    locations.add(location)
    classifications.update({cable:classification})

    mrns.add(cable)

    # remove page break
    body_filterd, page_match_count = re.subn(re_page,'',body)

    for r in referrer.split('|'):
        if len(r.strip()) > 0:
            edges.add((cable.upper(),r.upper()))
            ref_ids.add(r)
            if ref_cnt.has_key(r):
                ref_cnt[r] = ref_cnt[r] + 1
            else:
                ref_cnt[r] = 1

    match_ref = re.search(re_ref, body_filterd)
    if match_ref is not None:
        match_mrn = re.findall(re_mrn5, match_ref.group(2))
        for ignore, year, ignore, place, ignore, num, flag, ignore in match_mrn:
            # use current year if no year is given
            if len(year.strip()) == 0:
                year = str(tdate.strftime('%y'))
            elif len(year.strip()) == 4:
                year = year[2:4]

            txt_mrn = "%s%s%s" % (year.strip() , place.strip().upper().replace(' ',''), int(num.strip()) )
            # load them, but do the cross check later
            ref_from_text.update({cable:(txt_mrn,flag.strip())})
            ref_body_mrns.add(txt_mrn)

            if ref_body_cnt.has_key(txt_mrn):
                ref_body_cnt[txt_mrn] = ref_body_cnt[txt_mrn] + 1
            else:
                ref_body_cnt[txt_mrn] = 1

    subject_match = re.search(re_subject, body_filterd)
    if subject_match is not None:
        subject = subject_match.group(2).replace('\n','').strip()
    else:
        print "No Subject found in MRN %s" % cable
        subject = ''

    subjects.update({cable:subject})

    tags_match = re.search(re_tags, body)
    if tags_match is not None:
        tag = tags_match.group(1).replace('\n','').strip()
        subject_tags = re.findall(re_subject_tags, tag)
        program_tags = re.findall(re_program_tags, tag)
        ppl_tags = re.findall(re_ppl_tags, tag)
        for stag in subject_tags:
            tag_edges.add((cable,stag))
        for ktag in program_tags:
            tag_edges.add((cable,ktag))
    else:
        print "No TAGS found in MRN %s" % cable
        tag = ''
        
    tags.update({cable:tag})

    if count % 10000 == 0:
        print count

diff_ids = ref_ids.difference(mrns)
for d in diff_ids:
    diff_cnt[d] = ref_cnt[d]

# cross check for mrn extracted from body
# mrn exists in the header or
# mrn is counted at least twice
ref_ack = set()
captions = {}
for src_mrn, (txt_mrn, caption) in ref_from_text.iteritems():
    if txt_mrn in mrns or txt_mrn in ref_ids or ref_body_cnt[txt_mrn] > 1:
        ref_ack.add((src_mrn, txt_mrn))

    if (txt_mrn in mrns or txt_mrn in ref_ids) and len(caption.strip()) > 0:
        captions.update({txt_mrn: caption})

ref_body_new = ref_ack.difference(edges)

all_mrns = mrns.union(ref_body_mrns.union(ref_ids))

print "Lines read from csv: %s" % count
print "MRNs           : %s" % len(mrns)
print "Referenced MRNs: %s" % len(ref_ids)
print "          count: %s" % len(ref_cnt)
print "      from body: %s" % len(ref_body_mrns)
print "       together: %s" % len(all_mrns)
print "   with caption: %s" % len(captions)
print "Difference     : %s" % len(diff_ids)
print "Diff Count     : %s" % len(diff_cnt)
print "Edges          : %s" % len(edges)
print "   from body ok: %s" % len(ref_ack)
print "  from body new: %s" % len(ref_body_new)
print "Dates          : %s" % len(dates)
print "Subjects       : %s" % len(subjects)
print "Tags           : %s" % len(tags)
print "Locations      : %s" % len(locations)

# merge ref from body
edges.update(ref_body_new)
ref_ids.update(ref_body_mrns)

cf = file('data/cable_ids.list','w')
rf = file('data/ref_ids.list','w')
allf = file('data/all_ids.list','w')
df = file('data/diff_ids.list','w')
rcf = file('data/ref_cnt.list','w')
dcf = file('data/diff_cnt.list','w')
ef = file('data/edges.list','w')
datef = file('data/dates.list','w')
subf = file('data/subjects.list','w')
locf = file('data/locations.list','w')
tagsf = file('data/tag_edges.list','w')
classf = file('data/classifications.list','w')
captionsf = file('data/captions.list','w')

for i in sorted(mrns):
    cf.write('%s\n' % i)
cf.close()

for i in sorted(ref_ids):
    rf.write('%s\n' % i)
rf.close()

for i in sorted(all_mrns):
    allf.write('%s\n' % i)
allf.close()

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

for k,v in sorted(tag_edges):
    tagsf.write('%s %s\n' % (k,v))
tagsf.close()

for k,v in sorted(classifications.iteritems()):
    classf.write('%s %s\n' % (k,v))
classf.close()

for k,v in sorted(captions.iteritems()):
    captionsf.write('%s %s\n' % (k,v))
captionsf.close()

for i in sorted(locations):
    locf.write('%s\n' % i)
locf.close()

