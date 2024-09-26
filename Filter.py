import json
import re
import logging
import argparse

#-----------------------------------------------------
class Filter() :
  def __init__(self,args) :
    self.excludeUrlPatterns=[]
    if len(args.exclude) > 0 :
      xFiles=args.exclude.split(",")
      for xFile in xFiles :
        with open(xFile) as f:
          ex=json.load(f)
          self.excludeUrlPatterns += ex["excludePatterns"]
    if len(args.mexclude) > 0 :
      xPats=args.mexclude.split(",")
      for xPat in xPats :
        self.excludeUrlPatterns.append(xPat)

  #-----------------------------------------------------
  def keepUrl(self,entry) :
    url=entry["request"]["url"]
    for ex in self.excludeUrlPatterns :
    #print("{} {}".format(url,ex))
      if re.search(ex,url) :
      #print("Discard")
        return(False,ex)
    return(True,'')

