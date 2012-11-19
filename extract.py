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

# embassy names
emb = r'(ABIDJAN|ABU\s?DHABI|ABUJA|ACCRA|ADANA|ADDIS\s?ABABA|AITTAIPEI|AITTAIPIE|ALEXANDRIA|ALGIERS|ALMATY|AMEMBASSYHANOI|AMMAN|AMSTERDAM|ANILA|ANKARA|ANOI|ANTANANARIVO|APIA|AQNA|ARAJEVO|ASHGABAT|ASMARA|ASTANA|ASUNCION|ATANANARIVO|ATHENS|AUCKLAND|BAGHDAD|BAKU|BAMAKO|BANDARSERIBEGAWAN|BANGKOK|BANGOK|BANGUI|BANJUL|BARCELONA|BASRAH|BAU|BEIJIG|BEIJING|BEIRT|BEIRUT|BELFAST|BELGADE|BELGRADE|BELIZE|BELMOPAN|BERLIN|BERN|BISHKEK|BOGOTA|BONN|BRAILIA|BRASIIA|BRASILIA|BRATISLAVA|BRAZZAVILLE|BRIDGETOWN|BRUSELS|BRUSSELS|BRUSSLS|BRUSSQLS|BUCHAREST|BUDAPEST|BUENOS\s?AIRES|BUENOSQRES|BUJUMBURA|BUSSELS|CAIRO|CALCUTTA|CALGARY|CANBERRA|CAPETOWN|CARACAS|CASABLANCA|CDGENEVA|CHENGDU|CHENNAI|CHIANGMAI|CHISINAU|CIUDADJUAREZ|COLOMBO|CONAKRY|COPENHAEN|COPENHAGEN|COTONOU|CURACAO|DAKAR|DAMASCCUS|DAMASCUS|DARESSALAAM|DHAHRAN|DHAKA|DILI|DJIBOUTI|DOHA|DUBAI|DUBLIN|DULIN|DURBAN|DUSHANBE|DUSSELDORF|ECTION|FESTTWO|FLORENCE|FRANKFURT|FREETOWN|FSCCHARLESTON|FSINFATC|FUKUOKA|GABORONE|GENEVA|GEORGETON|GEORGETOWN|GRENADA|GUADALAJARA|GUANGZHOU|GUATEMALA|GUATEMLA|GUAYAQUIL|HALIFAX|HAMBURG|HAMILTON|HANOI|HARARE|HAVANA|HELSINKI|HERMOSILLO|HILLAH|HOCHIMINHCITY|HONGKOG|HONGKONG|HYDERABAD|IHARTOUM|INSHASA|IRANRPODUBAI|ISLAMABAD|ISTANBUL|IZMIR|JAKARTA|JEDDAH|JERUSALEM|JOHANNESBURG|KABUL|KADUNA|KAMPALA|KAPALA|KARACHI|KATHMANDU|KHARTOUM|KIEV|KIGALI|KINGSTON|KINHASA|KINSHAA|KINSHASA|KIRKUK|KOLKATA|KOLONIA|KOROR|KRAKOW|KUALALUMPUR|KUWAIT|KYIV|LAGOS|LAHORE|LAPAZ|LEIPZIG|LENINGRAD|LIBREVILLE|LILONGWE|LIMA|LINSK|LISBON|LJUBLJANA|LOME|LONDON|LUANDA|LUSAKA|LUXEMBOURG|MAAMA|MADRAS|MADRID|MAILA|MAJURO|MALABO|MANAGUA|MANAMA|MANILA|MAPUTO|MARSEILLE|MASERU|MATAMOROS|MBABANE|MELBOURNE|MERIDA|MEXICO|MILAN|MILSK|MINSI|MINSK|MOGADISHU|MONROVIA|MONTERREY|MONTEVIDEO|MONTREAL|MOSCOW|MOSUL|MUMBAI|MUNICH|MUSCAT|NAGOYA|NAHA|NAIROBI|NAPLES|NASSAU|NDJAENA|NDJAMENA|NEWDELHI|NIAMEY|NICOSIA|NOFORNMOGADISHU|NOGALES|NOUAKCHOTT|NOUKKCHOTT|NSSAU|NUEVOLAREDO|OSAKAKOBE|OSLO|OTTAWA|OUAGADOUGOU|PANAMA|PARAMARIBO|PARIS|PARISFR|PARTO|PERTH|PESHAWAR|PHNOMPENH|PODGORICA|PONTADELGADA|PORTAUPRINCE|PORTLOUIS|PORTMORESBY|PORTOFPAIN|PORTOFSPAIN|POTAUPRINCE|PRAGUE|PRAIA|PRETORIA|PRISTINA|QUEBEC|QUITO|QXICO|RABAT|RANGOON|RECIFE|REYKJAVIK|RIGA|RIODEJANEIRO|RIYADH|ROME|RPODUBAI|RUSSELS|SANAA|SANJOSE|SANODOMINGO|SANSALVADOR|SANTIAGO|SANTODOMINGO|SANTOOMINGO|SAO\s?PAULO|SAPPORO|SARAEVO|SARAJEVO|SECSTATE|SEOUL|SETION|SHANGHAI|SHENYANG|SIFIEDABUJA|SINGAPORE|SKOPJE|SOFIA|SOIA|STATE|STOCKHOLM|STPETERSBURG|STRASBOURG|SURABAYA|SUVA|SYDNEY|TAIPEI|TALLINN|TASHKENT|TBILISI|TEGUCIGALPA|TEHRAN|TELAVIV|THEHAGE|THEHAGU|THEHAGUE|THESSALONIKI|TIJUANA|TILISI|TIRANA|TOKYO|TORONTO|TRIPOLI|TUNIS|ULAANBAATAR|USOSCE|USTRGENEVA|USUNNEWYORK|VALLETTA|VANCOUVER|VATICAN|VIENNA|VIENTIANE|VILNIUS|VLADIVOSTOK|WARSAW|WASHDC|WELLINGTON|WINDHOEK|YAOUNDE|YEKATERINBURG|YEREVAN|ZAGREB)'

# list like A. B. C. / A) B) C)
mrn5_list = r'([A-Z][\s\W]{1,3})?'

# year as 0x 9x 20xx 19xx
mrn5_year = r'([0,6-9][0-9]|19[0-9]{2}|20[0-9]{2})?'
mrn5_num = r'([0-9]{1,10})'
# caption after the MRN like (NOTAL) or (EXDIS)
mrn5_caption = '(\s+\((NOTAL|EXDIS|NODIS|LIMDIS|ROGER|SIPDIS|STADIS|OIG|DISSENT|MED|DS)\))?'
mrn5_str = r'\W' + mrn5_list + mrn5_year + r'(\s)?' + emb + r'(\s)?' + mrn5_num + mrn5_caption + '\W'
re_mrn5 = re.compile(mrn5_str, re.I)

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
ref_from_text = set()
ref_body_mrns = set()
ref_body_cnt = {}

diff_cnt = {}
edges = set()
dates = {}
subjects = {}
classifications = {}
locations = set()
tags_edges = set()

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

    # match reference from body
    match_ref = re.search(re_ref, body_filterd)
    if match_ref is not None:
        match_mrn = re.findall(re_mrn5, match_ref.group(2))
        for ignore, year, ignore, place, ignore, num, caption, ignore in match_mrn:
            # use current year if no year is given
            if len(year.strip()) == 0:
                year = str(tdate.strftime('%y'))
            elif len(year.strip()) == 4:
                year = year[2:4]

            txt_mrn = "%s%s%s" % (year.strip() , place.strip().upper().replace(' ',''), int(num.strip()) )
            # load them, but do the cross check later
            ref_from_text.add((cable, txt_mrn, caption.strip().upper()))
            ref_body_mrns.add(txt_mrn)

            if ref_body_cnt.has_key(txt_mrn):
                ref_body_cnt[txt_mrn] = ref_body_cnt[txt_mrn] + 1
            else:
                ref_body_cnt[txt_mrn] = 1

    # match subject
    subject_match = re.search(re_subject, body_filterd)
    if subject_match is not None:
        subject = subject_match.group(2).replace('\n','').strip()
    else:
        print "No Subject found in MRN %s" % cable
        subject = ''

    subjects.update({cable:subject})

    # match TAGS
    tags_match = re.search(re_tags, body)
    if tags_match is not None:
        tags_line = tags_match.group(1).replace('\n','').strip()
        subject_tags = re.findall(re_subject_tags, tags_line)
        program_tags = re.findall(re_program_tags, tags_line)
        # ppl_tags = re.findall(re_ppl_tags, tag)
        for stag in subject_tags:
            tags_edges.add((cable,stag))
        for ktag in program_tags:
            tags_edges.add((cable,ktag))
    else:
        print "No TAGS found in MRN %s" % cable

    if count % 10000 == 0:
        print count


# cross check for mrn extracted from body
# mrn exists in the header or
# mrn is counted at least twice
ref_ack = set()
captions = set()
for src_mrn, txt_mrn, caption in ref_from_text:
    if txt_mrn in mrns or txt_mrn in ref_ids or ref_body_cnt[txt_mrn] > 1:
        ref_ack.add((src_mrn, txt_mrn))

    if (txt_mrn in mrns or txt_mrn in ref_ids) and len(caption) > 0:
        captions.add((txt_mrn, caption))

ref_body_new = ref_ack.difference(edges)

all_mrns = mrns.union(ref_body_mrns.union(ref_ids))

# merge ref from body
edges.update(ref_body_new)
ref_ids.update(ref_body_mrns)

# missing
missing_mrn = ref_ids.difference(mrns)

print "Lines read        : %s" % count
print "MRNs              : %s" % len(mrns)
print "Referenced MRNs   : %s" % len(ref_ids)
print "        from body : %s" % len(ref_body_mrns)
print "         together : %s" % len(all_mrns)
print "     with caption : %s" % len(captions)
print "          missing : %s" % len(missing_mrn)
print "Edges             : %s" % len(edges)
print "     from body ok : %s" % len(ref_ack)
print "    from body new : %s" % len(ref_body_new)
print "Dates             : %s" % len(dates)
print "Subjects          : %s" % len(subjects)
print "TAGS Edges        : %s" % len(tags_edges)
print "Locations         : %s" % len(locations)


cf = file('data/cable_ids.list','w')
rf = file('data/ref_ids.list','w')
allf = file('data/all_ids.list','w')
df = file('data/missing_mrn.list','w')
ef = file('data/edges.list','w')
datef = file('data/dates.list','w')
subf = file('data/subjects.list','w')
locf = file('data/locations.list','w')
tagsf = file('data/tags_edges.list','w')
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

for i in sorted(missing_mrn):
    df.write('%s\n' % i)
df.close()

for e in sorted(edges):
    ef.write('%s %s\n' % e)
ef.close()

for k,v in sorted(dates.iteritems()):
    datef.write('%s %s\n' % (k,v))
datef.close()

for k,v in sorted(subjects.iteritems()):
    subf.write('%s %s\n' % (k,v))
subf.close()

for k,v in sorted(tags_edges):
    tagsf.write('%s %s\n' % (k,v))
tagsf.close()

for k,v in sorted(classifications.iteritems()):
    classf.write('%s %s\n' % (k,v))
classf.close()

for k,v in sorted(captions):
    captionsf.write('%s %s\n' % (k,v))
captionsf.close()

for i in sorted(locations):
    locf.write('%s\n' % i)
locf.close()

