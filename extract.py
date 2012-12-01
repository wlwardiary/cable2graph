#!/usr/bin/env python
# GPLv3 by anonymous 2011-2012
#
# extract cable features from cables.csv
# - MRNs
# - references
# - TAGS
# - locations
# - subject
# - captions
# - all header data for ACP-126 and ACP-127
#   origin, from, to, info, routing, classifications, priorties and operating signals
# - dates
# 
# dirty data, be gentle
#

import csv, re, sys, time
from os import environ, path
from datetime import datetime

# set timezone fixed to UTC for the date parser
environ['TZ'] = 'UTC'
time.tzset()

if len(sys.argv) < 2:
    sys.stderr.write("Usage: %s /path/to/cables.csv [LIMIT]\n" % sys.argv[0])
    sys.exit(1)

limit = None
if len(sys.argv) == 3:
    limit = int(sys.argv[2])

source = sys.argv[1]
if not path.exists(source):
    sys.stderr.write("Error: source %s does not exist.\n" % source)
    sys.exit(1)

#
# compile all the regex magic
#

# remove page break from body to avoid problems 
# when subject is spaning multiple pages
re_page = re.compile(r'^(\ {1,30}(CONFIDENTIAL|SECRET|UNCLASSIFIED)\s+){1,3}^PAGE\s+[0-9]{2}.*\n', re.M)

# multi line reference from body
# second regex is matching MRN, see below
re_ref = re.compile(r'^(REF|REFS|Ref|RETELS|REFTEL):([\s\S]*?)(?=(?:\n\s\n)|1\.|SIPDIS|Summary|SUMMARY|Classified\ By|CLASSIFIED\ BY|Sensitive\ But\ Unclassified|SENSITIVE\ BUT\ UNCLASSIFIED)', re.M)

# parse TAGS over multiple lines with a couple of stop words
re_tags = re.compile(r'^TAGS:([\s\S]*?)(?=(?:\n\s\n)|(?:CLASSIFIED\ BY|Classified\ by|REF:|REFS:|Ref:|RETELS:|REFTEL:|REF\ :|SUBJECT:|Subject:|SUBJ:|Subj:|E\.O\.|\*\*\*\*|FINAL\ SECTION\ OF|SECRET\ |CONFIDENTIAL\ |UNCLASSIFIED\ |COMBINE:))', re.M)

# load valid TAGS
# source cabletags website
all_subject_tags = [ l.strip() for l in open('data/tags.subject').readlines() ] 
all_program_tags = [ l.strip() for l in open('data/tags.program').readlines() ] 

re_subject_tags = re.compile(r'(' + '|'.join(all_subject_tags) + r')',re.M)
re_program_tags = re.compile(r'(' + '|'.join(all_program_tags) + r')',re.M)

# people mentioned in the TAGS field
# re_ppl_tags = re.compile(r'(OVIP|OREP|SP|JO|HO|CO|RO|PINR|OTRA|PREL|APER|CASC|CLOK|CVIS|DR|EG|FR|MX|NI|PM|PA|SCE|SY|UN|US|USPTO|VM)(\W+)?\(.*\)')

# try to match a valid MRN o_O
# re_mrn1 = re.compile(r'\W+[A-Z]\W+([0-9]{2,4})?([a-zA-Z\s]{3,12})\s([0-9]{1,8})')
# re_mrn2 = re.compile(r'([0-9]{2,4})?([a-zA-Z]{3,18})\s([0-9]{1,8})')
# re_mrn3 = re.compile(r'\b([A-Z][\s\W]{1,3})?([0-9]{2,4})?\s?([a-zA-Z\s]{3,18})\s?([0-9]{1,8})\W')
# re_mrn4 = re.compile(r'\b([A-Z][\s\W]{1,3})?([0-9]{2,4})?\s?([a-zA-Z\s]{3,18})\s?([0-9]{1,8})(\s+\(NOTAL|EXDIS|NODIS|Notal|Exdis|Nodis\))?\W')

# embassy names with optional space in city names
re_emb = (
r'(ABIDJAN|ABU\s?DHABI|ABUJA|ACCRA|ADANA|ADDIS\s?ABABA|AITTAIPEI|AITTAIPIE|ALEXANDRIA|ALGIERS|ALMATY|AMEMBASSYHANOI|AMMAN|AMSTERDAM|ANILA|ANKARA|ANOI|ANTANANARIVO|APIA|AQNA|ARAJEVO|ASHGABAT|ASMARA|ASTANA|ASUNCION|ATANANARIVO|ATHENS|AUCKLAND|'
'BAGHDAD|BAKU|BAMAKO|BANDARSERIBEGAWAN|BANGKOK|BANGOK|BANGUI|BANJUL|BARCELONA|BASRAH|BAU|BEIJIG|BEIJING|BEIRT|BEIRUT|BELFAST|BELGADE|BELGRADE|BELIZE|BELMOPAN|BERLIN|BERN|BISHKEK|BOGOTA|BONN|BRAILIA|BRASIIA|BRASILIA|BRATISLAVA|BRAZZAVILLE|BRIDGETOWN|BRUSELS|BRUSSELS|BRUSSLS|BRUSSQLS|BUCHAREST|BUDAPEST|BUENOS\s?AIRES|BUENOSQRES|BUJUMBURA|BUSSELS|'
r'CAIRO|CALCUTTA|CALGARY|CANBERRA|CAPETOWN|CARACAS|CASABLANCA|CDGENEVA|CHENGDU|CHENNAI|CHIANGMAI|CHISINAU|CIUDADJUAREZ|COLOMBO|CONAKRY|COPENHAEN|COPENHAGEN|COTONOU|CURACAO|' 
r'DAKAR|DAMASCCUS|DAMASCUS|DARESSALAAM|DHAHRAN|DHAKA|DILI|DJIBOUTI|DOHA|DUBAI|DUBLIN|DULIN|DURBAN|DUSHANBE|DUSSELDORF|'
r'FESTTWO|FLORENCE|FRANKFURT|FREETOWN|FSCCHARLESTON|FSINFATC|FUKUOKA|' 
r'GABORONE|GENEVA|GEORGETON|GEORGETOWN|GRENADA|GUADALAJARA|GUANGZHOU|GUATEMALA|GUATEMLA|GUAYAQUIL|' 
r'HALIFAX|HAMBURG|HAMILTON|HANOI|HARARE|HAVANA|HELSINKI|HERMOSILLO|HILLAH|HOCHIMINHCITY|HONGKOG|HONGKONG|HYDERABAD|'
r'IHARTOUM|INSHASA|IRANRPODUBAI|ISLAMABAD|ISTANBUL|IZMIR|'
r'JAKARTA|JEDDAH|JERUSALEM|JOHANNESBURG|'
r'KABUL|KADUNA|KAMPALA|KAPALA|KARACHI|KATHMANDU|KHARTOUM|KIEV|KIGALI|KINGSTON|KINHASA|KINSHAA|KINSHASA|KIRKUK|KOLKATA|KOLONIA|KOROR|KRAKOW|KUALALUMPUR|KUWAIT|KYIV|'
r'LAGOS|LAHORE|LAPAZ|LEIPZIG|LENINGRAD|LIBREVILLE|LILONGWE|LIMA|LINSK|LISBON|LJUBLJANA|LOME|LONDON|LUANDA|LUSAKA|LUXEMBOURG|'
r'MAAMA|MADRAS|MADRID|MAILA|MAJURO|MALABO|MANAGUA|MANAMA|MANILA|MAPUTO|MARSEILLE|MASERU|MATAMOROS|MBABANE|MELBOURNE|MERIDA|MEXICO|MILAN|MILSK|MINSI|MINSK|MOGADISHU|MONROVIA|MONTERREY|MONTEVIDEO|MONTREAL|MOSCOW|MOSUL|MUMBAI|MUNICH|MUSCAT|'
r'NAGOYA|NAHA|NAIROBI|NAPLES|NASSAU|NDJAENA|NDJAMENA|NEWDELHI|NIAMEY|NICOSIA|NOFORNMOGADISHU|NOGALES|NOUAKCHOTT|NOUKKCHOTT|NSSAU|NUEVOLAREDO|'
r'OSAKAKOBE|OSLO|OTTAWA|OUAGADOUGOU|'
r'PANAMA|PARAMARIBO|PARIS|PARISFR|PARTO|PERTH|PESHAWAR|PHNOMPENH|PODGORICA|PONTADELGADA|PORTAUPRINCE|PORTLOUIS|PORTMORESBY|PORTOFPAIN|PORTOFSPAIN|POTAUPRINCE|PRAGUE|PRAIA|PRETORIA|PRISTINA|'
r'QUEBEC|QUITO|QXICO|'
r'RABAT|RANGOON|RECIFE|REYKJAVIK|RIGA|RIODEJANEIRO|RIYADH|ROME|RPODUBAI|RUSSELS|'
r'SANAA|SANJOSE|SANODOMINGO|SANSALVADOR|SANTIAGO|SANTODOMINGO|SANTOOMINGO|SAO\s?PAULO|SAPPORO|SARAEVO|SARAJEVO|SECSTATE|SEOUL|SETION|SHANGHAI|SHENYANG|SIFIEDABUJA|SINGAPORE|SKOPJE|SOFIA|SOIA|STATE|STOCKHOLM|STPETERSBURG|STRASBOURG|SURABAYA|SUVA|SYDNEY|'
r'TAIPEI|TALLINN|TASHKENT|TBILISI|TEGUCIGALPA|TEHRAN|TELAVIV|THEHAGE|THEHAGU|THEHAGUE|THESSALONIKI|TIJUANA|TILISI|TIRANA|TOKYO|TORONTO|TRIPOLI|TUNIS|'
r'ULAANBAATAR|USOSCE|USTRGENEVA|USUNNEWYORK|'
r'VALLETTA|VANCOUVER|VATICAN|VIENNA|VIENTIANE|VILNIUS|VLADIVOSTOK|'
r'WARSAW|WASHDC|WELLINGTON|WINDHOEK|YAOUNDE|YEKATERINBURG|YEREVAN|ZAGREB)'
)

# list like A. B. C. / A) B) C)
mrn5_list = r'([A-Z][\s\W]{1,3})?'

# year as 0x 9x 20xx 19xx
mrn5_year = r'([0,6-9][0-9]|19[0-9]{2}|20[0-9]{2})?'
mrn5_num = r'([0-9]{1,10})'
# caption after the MRN like (NOTAL) or (EXDIS)
mrn5_caption = '(\s+\((NOTAL|EXDIS|NODIS|STADIS)\))?'
mrn5_str = r'\W' + mrn5_list + mrn5_year + r'(\s)?' + re_emb + r'(\s)?' + mrn5_num + mrn5_caption + '\W'
re_mrn5 = re.compile(mrn5_str, re.I)

# find subject over multiple lines
# line starts with SUBJECT:
# followed by space and non-space greedy matching which can span multiple lines
# until two new lines or other body elements
re_subject = re.compile(r'^(SUBJ|SUBJECT):([\s\S]*?)(?=(?:\n\s\n)|(?:CLASSIFIED BY|Classified by|REF:|REFS:))', re.M)

# caption area goes from the start of the body until E.O.
re_caption = re.compile(r'(.*)^E\.(O|0)\.', re.S|re.M)

# ACP-127 FL1 start of message indicator
# two char transfer station
# ADI, AJI, AYI, BGI, BSI, BSO, DOI, DRI,FRI, JII, KEI, LII, LOI, MDI, MZI, PCI, SFI, UNI, XRO, XYZ
# exist in the cables.
# I for incoming, O for outgoing and Z for ?
re_acp127_som = re.compile(r'VZCZC([A-Z]{2}[Z,I,O])([0-9]{4})')

# ACP-127 FL2 Addressees
# First two letter Priority
# Second Routing, can be multi line
# See: ROUTING INDICATOR DELINEATION TABLE from ACP-121
# OO RUEHC RHRMDAB RUCNRAQ RUEKJCS RUENAAA RHEHNSC
# RUEKJCS RUCNDT RUCXONI RUCJACC RUHPFTA RHRMABI RUWDXEU RUEHDE
re_acp127_addr = re.compile(r'^(ZZ|OO|PP|RR)\ ((?:[QRU][A-IK-QS-UW-Z][A-Z]{1,5}\s?)+)', re.M)

# ACP-127 FL3 Originator
# originating station's routing indicator (osri), station serial number (ssn) and time of transmission (tot)
# day of the year, hour and minute %j%H%M
# Examples:
# DE RUEHLL #0524 2351212
# DE RUZDSVC #0741 2611349
re_acp127_origin = re.compile(r'^DE\ ([QRU][A-IK-QS-UW-Z][A-Z]{1,5}) #([0-9]{4})(/([0-9]{2}))?(\ [0-9]{3,7})?',re.M)

# ACP-127 FL4 classification line
# Examples:
# ZNR UUUAA ZZH
# ZNR UUUUU ZFD
# ZNY SSSSS/BBBBB ZZH
#
# AA in UUUAA is TRC Transmission Release Code
# A - Australia, 
# B - British, 
# C - Canada, 
# O - Japan, 
# U - United States (from non. U.S. interfaces)
# X - all other NATO
#
# SSSSS/BBBBB: B indicates Military
# ZNY SSSBB/FFFFF, ZNY CCCBB/FFFFF, or ZNY TTTBB/FFFFF would be TOP SECRET for UK
# 
# ZZH: from Department of State offices
# ZFD: This message is a suspected duplicate
# ZZK: NIACT
# ZDF: Received
# ZOC: Station(s) called relay this message to addressees for whom you are responsible
# ZUI: Your attention is invited to...
# ZFR: cancel
# ZOJ: This is corrected version number.
# ZEL: This message is a correction
# ZEX: book message

re_acp127_clss = re.compile(r'^ZN[R,Y]\ ([U,E,C,S,T]{5}|[U,E,C,S,T]{3}[A,B,C,O,U,X]{2})(/[B,F]{5})?(\ Z[A-Z]{2})+', re.M)

# ACP-126 date time group
# Z,O,P,R == Flash, Immediate, Priority, Routine
# optional Z.... in the end is operation signaling for night actions and such
# Examples
# O P 180800Z MAR 08 ZDS
# O P 260738Z APR 08
# P 011533Z MAY 09

re_acp126_dtg = re.compile(r'^([ZOPR\ ]{4})([0-9]{6}Z [A-Z]{3} [0-9]{2})( Z[A-Z0-9]+)?', re.M)

#
# normalize station names
#

# optional start with TO or INFO followed by space
re_str_pre = r'^((TO|INFO)\ +)?'

# routing indicator
re_str_ri  = r'([QRU][A-IK-QS-UW-Z][A-Z]{1,5})'

# we do greedy matching, (*?) so it 
# must follow a / or new line or...
re_str_end = r'(?=\/|$|NIACT|IMMEDIATE|PRIORITY|ROUTINE|[0-9]{1,6})'

# plain language single destination
# Examples:
# TO USMISSION USUN NEWYORK NIACT IMMEDIATE
# INFO AMEMBASSY PARIS
# SECSTATE WASHDC IMMEDIATE 7102

re_pl_single = re.compile(re_str_pre + r'([A-Z\ \-]*?)' + re_str_end, re.M)

# plain language collective
re_pl_collective = re.compile( re_str_pre + r'([A-Z\ \-]*?COLLECTIVE)' + re_str_end, re.M)

# single station name with routing indicator
re_ri_single = re.compile(re_str_pre + re_str_ri + '/([A-Z\ \-]*?)' + re_str_end, re.M)

# collective with routing indicator
re_ri_collective = re.compile(re_str_pre + re_str_ri + r'/([A-Z\ \-]*?COLLECTIVE)' + re_str_end, re.M)

# routing indicator to plain language and the reverse
ri2pl = dict()
pl2ri = dict()

for ri,pl in [ ( l.split(' ', 1) ) for l in open('data/routing.codes').readlines() ]:
    ri2pl[ri.strip()] = pl.strip()
    pl2ri[pl.strip()] = ri.strip()

#
# functions
#

# parse the ACP-126 message header
def parse_acp126(header):
    parsed = dict()

    match_dtg = re.match(re_acp126_dtg, header)
    if match_dtg is None:
        return False
    else:
        parsed['precedence'] = match_dtg.group(1).strip().split(' ')
        if match_dtg.group(3) is not None:
            parsed['operating_signal'] = match_dtg.group(3).strip()
    
    lines = header.split('\n')
    to_start = None
    to_end = None
    info_start = None
    for num, line in enumerate(lines):
        if num == 0:
            continue
        if line[0:3] == 'FM ' and 'FM' not in parsed:
            parsed['FM'] = line[3:]
            continue
        if line[0:3] == 'TO ' and not to_start:
            to_start = num
            continue
        if line[0:5] == 'INFO ' and not info_start:
            to_end = num
            info_start = num

    if to_start and to_end:
        parsed['TO'] = [ line.strip() for line in lines[to_start:to_end ] if len(line.strip()) > 0 ] 

    if to_start and not to_end and not info_start:
        parsed['TO'] = [ line.strip() for line in lines[to_start:] if len(line.strip()) > 0 ]

    if info_start:
        parsed['INFO'] = [ line.strip() for line in lines[info_start:] if len(line.strip()) > 0 ]

    return parsed

# parse ACP-127 msg header
def parse_acp127(header):
    parsed = dict()

    match_som = re.match(re_acp127_som, header)
    if match_som is None:
        return False

    # FL2
    match_addr = re.search(re_acp127_addr, header)
    if match_addr is not None and match_addr.group(2) is not None:
        parsed['addr'] = [ a.strip() for a in match_addr.group(2).strip().split() ]

    # FL3
    match_origin = re.search(re_acp127_origin, header)
    if match_origin is not None:
        parsed['osri'] = match_origin.group(1)
        parsed['ssn'] = int(match_origin.group(2))
        if match_origin.group(4) is not None:
            parsed['part'] = int(match_origin.group(4))
        parsed['tot'] = match_origin.group(5)
    
    # FL4
    match_clss = re.search(re_acp127_clss, header)
    if match_clss is not None:
        parsed['classification'] = match_clss.group(1).strip()
        if match_clss.group(2) is not None:
            parsed['classification_external'] = match_clss.group(3).strip()
        if match_clss.group(3) is not None:
            parsed['classification_operating_signal'] = match_clss.group(3).strip()
    # FL5
    # date time group same as acp126
    match_dtg = re.search(re_acp126_dtg, header)
    if match_dtg is not None:
        parsed['precedence'] = match_dtg.group(1).strip().split(' ')
        if match_dtg.group(3) is not None:
            parsed['dtg_operating_signal'] = match_dtg.group(3).strip()

    to_start = None
    to_end = None
    info_start = None
    lines = header.split('\n')
    for num, line in enumerate(lines):
        # skip the first, already parsed with regex
        if num in [0,1,2,3,4]:
            continue

        if line[0:3] == 'FM ':
            parsed['FM'] = line[3:].strip()

        if line[0:3] == 'TO ' and not to_start:
            to_start = num
            continue

        if line[0:5] == 'INFO ' and not info_start:
            to_end = num
            info_start = num

    if to_start and to_end:
        parsed['TO'] = [ line.strip() for line in lines[to_start:to_end ] if len(line.strip()) > 0 ] 

    if to_start and not to_end and not info_start:
        parsed['TO'] = [ line.strip() for line in lines[to_start:] if len(line.strip()) > 0 ]

    if info_start:
        parsed['INFO'] = [ line.strip() for line in lines[info_start:] if len(line.strip()) > 0 ]

    return parsed

# check raw input for valid station name
def match_station(raw):
    # match the most restrictive first
    match_ri_collective = re.match(re_ri_collective, raw)
    if match_ri_collective is not None:
        return match_ri_collective.group(3).strip()

    match_ri_single = re.match(re_ri_single, raw)
    if match_ri_single is not None:
        return match_ri_single.group(3).strip()

    match_pl_collective = re.match(re_pl_collective, raw)
    if match_pl_collective is not None:
        m = match_pl_collective.group(3).strip()
        if m in pl2ri:
            return pl2ri[m]
        else:
            return m

    match_pl_single = re.match(re_pl_single, raw)
    if match_pl_single is not None:
        m = match_pl_single.group(3).strip()
        if m in pl2ri:
            return pl2ri[m]
        else:
            return m

    return False    

#
# init data vars
#

# list of MRNs contained in the cables.csv
mrns = set()

# MRN reference's from csv header
ref_ids = set()
ref_cnt = {}

# MRN reference's from cable text body via regex
ref_from_text = set()
ref_body_mrns = set()
ref_body_cnt = {}

# MRN -> MRN relation for the graph
# set of tuples
edges = set()

# all cable dates as POSIX MRN -> timestamp
dates = {}

# subjects as MRN -> subject
subjects = {}

# classifications for each MRN
classifications = {}

# locations from the csv header
locations = set()

# MRN -> TAGS relation
# set of tuples
tags_edges = set()
    
# routings
from_to= set()

#
# start reading the csv
#
csv.field_size_limit(131072*2)

try:
    content = csv.reader(open(source), delimiter=',', quotechar='"', escapechar='\\')
except IOError:
    sys.stderr.write("Error: could not open source %s\n" % source)
    sys.exit(1)

count = 0
for row in content:
    count = count + 1
    if limit is not None and count > limit:
        sys.stderr.write("Limit %d reached.\n" % limit)
        sys.exit(0)

    # read csv values
    line_num, cabledate, mrn, location, classification, referrer, head, body = row

    # parse header
    # either:
    # - valid ACP-126 header (~5936 cables)
    # - valid ACP-127 header (~193225 cables)
    # - only partial record (~49082 cables)
    # - valid ACP 126/127 later in the header

    acp127 = parse_acp127(head)
    acp126 = parse_acp126(head)

    if acp127:
        acp12x = acp127
    elif acp126:
        acp12x = acp126
    else:
        acp12x = False

    if acp12x:
        if 'osri' in acp12x:
            osri = acp12x['osri']
        elif 'FM' in acp12x and acp12x['FM'] in pl2ri:
            osri = pl2ri[acp12x['FM']]
        else:
            osri = False
            sys.stderr.write("INFO: No OSRI in MRN %s.\n" % mrn)

        if osri and 'addr' in acp12x:
            for addr in acp12x['addr']:
                if osri != addr:
                    from_to.add((mrn, osri, addr))

        if osri and 'TO' in acp12x:
            for to in acp12x['TO']:
                ms = match_station(to)
                if ms:
                    if osri != ms:
                        from_to.add((mrn, osri, ms))
                else:
                    sys.stderr.write("INFO: Invalid TO line in MRN %s: (%s)\n" % (mrn, to))

        if osri and 'INFO' in acp12x:
            for info in acp12x['INFO']:
                ms = match_station(info)
                if ms:
                    if osri != ms:
                        from_to.add((mrn, osri, ms))
                else:
                    sys.stderr.write("INFO: Invalid INFO line in MRN %s: (%s)\n" % (mrn, info))

    #pos = body.find('E.O.')
    #if pos > 0:
    #    print mrn, body[0:pos].replace('\n','').strip()

    # pos_banner = head.find('This record is a partial extract of the original cable. The full text of the original cable is not available.')

    #match_caption = re.match(re_caption, body)
    #if match_caption is not None:
    #    print mrn, match_caption.group(0)
    #del body, match_caption

    # parse cable date into POSIX timestamp
    tdate = datetime.strptime(cabledate.strip(), '%m/%d/%Y %H:%M')
    timestamp = int(time.mktime(tdate.timetuple()))
    dates.update({mrn:timestamp})

    locations.add(location)
    classifications.update({mrn:classification})
    mrns.add(mrn)

    # remove page break
    body_filterd, page_match_count = re.subn(re_page,'',body)

    for r in referrer.split('|'):
        if len(r.strip()) > 0:
            edges.add((mrn.upper(),r.upper()))
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
            ref_from_text.add((mrn, txt_mrn, caption.strip().upper()))
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
        sys.stderr.write("INFO: No Subject found in MRN %s\n" % mrn)
        subject = ''

    subjects.update({mrn:subject})

    # match TAGS
    tags_match = re.search(re_tags, body)
    if tags_match is not None:
        tags_line = tags_match.group(1).replace('\n','').strip()
        subject_tags = re.findall(re_subject_tags, tags_line)
        program_tags = re.findall(re_program_tags, tags_line)
        # ppl_tags = re.findall(re_ppl_tags, tag)
        for stag in subject_tags:
            tags_edges.add((mrn,stag))
        for ktag in program_tags:
            tags_edges.add((mrn,ktag))
    else:
        sys.stderr.write("INFO: No TAGS found in MRN %s\n" % mrn)

    if count % 10000 == 0:
        sys.stderr.write("%s lines read\n" % count)

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
print "From -> To/Info   : %s" % len(from_to)


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
fromtof = file('data/from_to.list','w')

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

for m,s,t in sorted(from_to):
    fromtof.write('%s\t%s\t%s\t%s\n' % (m,s,t,dates[m]))
fromtof.close()
