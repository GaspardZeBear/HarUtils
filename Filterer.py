import json
import re
import logging
import argparse
from Filter import *
from EntriesLog import *

class Filterer() :

  def __init__(self,args) :
    self.args=args
    self.filter()

  def filter(self) :
    with open(self.args.file) as f:
      data = json.load(f)
  #print(data)
    for d in data["log"]["pages"] :
      print(d["id"])
      print(d["title"])
  
    entries=[]
    excludedUrls=[]
    filter=Filter(self.args)
    entriesLog=EntriesLog()
    stats={
      'total' : len(data["log"]["entries"]),
      'kept' : 0,
      'discarded' : 0,
      }
    for idx,e in enumerate(data["log"]["entries"]) :
      keep,reason=filter.keepUrl(e)
      if keep :
        entries.append(e)
        stats['kept'] += 1
        entriesLog.logEntry(stats,idx,e)
      else :
        stats['discarded'] += 1
        excludedUrls.append(" match  " + reason + " for " +  e["request"]["url"])
  
    for x in excludedUrls :
      print("Discarded  " + x)
  
    entriesLog.printAll()
  
    if len(self.args.out) > 0 :
      data["log"]["entries"]=entries
      newJson=open(self.args.out,"w")
      newJson.write(json.dumps(data))
      newJson.close()
  
