#!/usr/bin/env python
# guess the upper and lower date range of missing cables
# by using the last and next cable in the row
# example:
# 99STATE1 1999-01-01
# 99STATE2 missing cable possibly created between 
#          1999-01-01 and 1999-01-05
# 99STATE3 1999-01-05
#
import re
from datetime import timedelta
re_cable_id = re.compile(r'([0-9]{2,4}[a-zA-Z]{3,12})([0-9]{1,8})')

dates = dict()   # all dates
missing = dict() # missing cables
ignore = set()   # list of cables that are not in "order"
                 # can not be used for prediction

dfh = open('data/dates.list')
for line in dfh.readlines():
    cableid, timestamp = line.split()
    m = re.match(re_cable_id, cableid)
    if m is not None:
        year_emb = m.group(1)
        num = int(m.group(2))
    if dates.has_key(year_emb):
        dates[year_emb].update({num: int(timestamp)})
    else:
        dates[year_emb] = {num: int(timestamp)}

mfh = open('data/missing_mrn.list')
for line in mfh.readlines():
    m = re.match(re_cable_id, line.strip())
    if m is not None:
        year_emb = m.group(1)
        num = int(m.group(2))
    if missing.has_key(year_emb):
        missing[year_emb].append(num)
    else:
        missing[year_emb] = list()
        missing[year_emb].append(num)

# find cables to ignore
for k, v in dates.iteritems():
    last_ts = 0
    for num, ts in sorted(v.iteritems()):
        if last_ts > ts: 
            ignore.add('%s%s' % (k,num))
        last_ts = ts

durations = []
for year_emb, numlist in missing.iteritems():
    for num in sorted(numlist):
        if dates.has_key(year_emb):
            last_num = 0
            for existing_num in sorted(dates[year_emb].iterkeys()):
                if '%s%s' % (year_emb, existing_num) in ignore:
                    continue

                if last_num > 0 and existing_num > num and last_num < num:
                    last_ts = dates[year_emb][last_num]
                    next_ts = dates[year_emb][existing_num]
                    duration = next_ts - last_ts
                    if duration < 0:
                        continue
                    days = timedelta(seconds=duration).days
                    if days > 90: # not much of a value
                        continue
                    durations.append(days)
                    new_ts = last_ts + (duration / 2)
                    print "%s%s %s" % (year_emb, num, new_ts)
#                    print "%s%s %s %s %s %s -> %s" % (
#                        year_emb, 
#                        num, 
#                        last_ts,
#                        next_ts,
#                        duration,
#                        days,
#                        new_ts) 
                            
                last_num = existing_num

#average = float(sum(durations)) / len(durations)
