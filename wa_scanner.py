#!/usr/bin/python

from parser import api
from ns import id_str
import urllib2
import time
import json
from operator import itemgetter as get

import argparse

parser = argparse.ArgumentParser(description="Scan region")
parser.add_argument('-u', '--user', metavar='USER', required=True, help='a nation name, email, or web page to identify the user as per item 1 of the NS API Terms of Use: http://www.nationstates.net/pages/api.html#terms')
parser.add_argument('-r', '--region', metavar='REGION', required=True, help='the region to scan')
parser.add_argument('-o', '--output', metavar='FILE', help='the file to save the results to (otherwise prints raw JSON to screen)')
parser.add_argument('-i', '--influential-url', metavar='URL', help='an (optional) url to fetch a newline-delimited text file of the non-minnows in the region')
parser.add_argument('-a', '--all', nargs="?", help='scan all nations of the region, not just the WA nations')
parser.add_argument('-c', '--columns', nargs="+", choices=["endorsers","endorsees","influential"], default=["endorsers","endorsees"], help='columns to collect (top endorsers = nations who endorse the most, top endorsees = top recipients of endorsements)')
parser.add_argument('-R', '--rows', default=25, help='number of rows to collect (default = collect top 25 for each column)')

args = parser.parse_args()

api.user_agent = "Trawler Python Region Scan (operated by {})".format(args.user)

def get_nation_endos(nation):
  xmlnat = api.request({'nation':nation,'q':('endorsements','wa','name','censusscore-65')})
  endos = xmlnat.find('ENDORSEMENTS').text
  name = xmlnat.find('NAME').text
  spdr = int(xmlnat.find('CENSUSSCORE').text)
  endocount = endos.count(',')+1 if endos else 0
  return {'name':nation,'Name':name,'endos':endocount,'endorsers':endos.split(',') if endos else (),'influence_score':spdr}


xmlreg = api.request({'region':id_str(args.region),'q':'nations'})
residents = xmlreg.find('NATIONS').text.split(':')
if not args.all:
    resident_set = set(residents)
    xmlwa = api.request({'wa':'1','q':'members'})
    all_wa_nations = xmlwa.find('MEMBERS').text.split(',')
    wa_nation_set=set(all_wa_nations)

if args.influential_url:
    influential_nation_names = map( str.strip, urllib2.urlopen(args.influential_url).readlines() )

scanned_nations = []
endorser_counts = {}
if args.all:
  to_scan = resident_set
else:
  to_scan = resident_set & wa_nation_set

for nat in to_scan:
  scanned_nations.append(nat)
  endorser_counts[nat]=0

infos={}

todo={}


for nat in scanned_nations:
  endos = get_nation_endos(nat)
  for endorser in endos['endorsers']:
    endorser_counts[endorser] += 1
  del endos['endorsers']
  infos[nat]=endos

for nat in scanned_nations:
  infos[nat]['endos_given'] = endorser_counts[nat]

if args.influential_url:
  for nation in influential_nation_names:
    nat=id_str(nation)
    if nat not in wa_nation_set:
      if nat in resident_set:
        endos = get_nation_endos( nat )
        del endos['endorsers']
        endos['endos_given']=0
        infos[nat]=endos

res={}
rows = args.rows
cols = args.columns
col_keys={'endorsers':'endos_given','endorsees':'endos','influential':'influence_score'}
for col in cols:
    res[col]= sorted(infos.values(),key=lambda info: info[col_keys[col]],reverse=True)[0:rows]

res = dict(map(lambda item: (item[0],map(get('name'),item[1])), res.iteritems()))
res['pool']=map( lambda n: infos[n], apply(set.union,map(lambda l: set(l),res.values())) )

if args.output:
  outf=open(args.output,"w+")
else:
  import sys
  outf = sys.stdout

json.dump(res,outf,separators=(',', ':'),sort_keys=True)
if not args.output:
  print ""
