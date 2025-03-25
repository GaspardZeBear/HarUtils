import json
import base64
import sys
import re
import logging
from Utils import *

#=================================================================================
class Criterias() :

  def __init__(self,args) :
    self.criterias={
      "blocked":float(args.blocked),
      "wait":float(args.wait),
      "receive":float(args.receive),
      "send":float(args.send),
      "latency":float(args.latency),
      "size":float(args.size),
      "ssl":float(args.ssl),
      "dns":float(args.dns),
      "connect":float(args.connect)
      }
    # Just to know if at least one criteria is set
    self.apply=0
    for a in self.criterias.keys() :
      self.apply += float(self.criterias[a])

  # if criteria must be tested (value > 0 in self.criterias) 
  # and one criteria value exceeds threshold keep 
  def filterCriteriasKeep(self,harCriterias) :
    if self.apply ==0 :
      return(True)

    logging.debug(f'{harCriterias}')
    for criteria in harCriterias.keys()  :
      if criteria in self.criterias :
        target=self.criterias[criteria]
        if target > 0  :
          if harCriterias[criteria] > 0 :
            if harCriterias[criteria] > target :
              return(True)
    return(False)

#=================================================================================
class Explorer() :

  def __init__(self,args) :
    self.args=args
    self.urlBegin=int(args.urlBegin)
    self.urlEnd=int(args.urlEnd)
    self.textTrunc=int(args.textTrunc)
    self.size=int(args.size)
    self.name=args.name
    self.timing=args.timing
    self.blocked=float(args.blocked)
    self.wait=float(args.wait)
    self.receive=float(args.receive)
    self.latency=float(args.latency)
    self.ssl=float(args.ssl)
    self.dns=float(args.dns)
    self.connect=float(args.connect)
    self.timings=Criterias(args)
    self.includeRegexp=self.args.minclude if len(self.args.minclude) > 0 else '.*'
    self.excludeRegexp=self.args.mexclude if len(self.args.mexclude) > 0 else ''
    self.idomainRegexp=self.args.idomain if len(self.args.idomain) > 0 else '.*'
    self.xdomainRegexp=self.args.xdomain if len(self.args.xdomain) > 0 else ''
    self.showHeaders=args.showHeaders
    self.showResponseContent=args.showResponseContent
    self.range=args.range
    self.startIdx=0
    self.endIdx=0
    self.hardisplay=args.hardisplay
    if len(self.range) > 0 :
      t=self.range.split(",")
      self.startIdx=int(t[0])
      if len(t) == 1 :
        self.endIdx=self.startIdx+1
      else :
        self.endIdx=int(t[1])
    self.pages()
    self.requests()

  #-----------------------------------------------------------------------------------------
  def getIdToDisplay(self,url) :
    id=url[self.urlBegin:self.urlEnd]
    if self.name :
      t=re.split("/",url)
      if len(t) == 3 :
        t[2]="*"
      id=t[0]+'//'+t[1]+t[2]+'...'+t[-1]
    return(id)

  #-----------------------------------------------------------------------------------------
  def filterUrlKeep(self,url) :
    if len(self.excludeRegexp) > 0 and re.search(self.excludeRegexp,url) :
      return(False)
    if not re.search(self.includeRegexp,url) :
      return(False)
    return(True)

  #-----------------------------------------------------------------------------------------
  def filterDomainKeep(self,url) :
    x=re.split("/",url)
    #print(f'{x}')
    if len(x) > 2 :
      if not re.search(self.idomainRegexp,x[2]) :
        return(False)
      if len(self.xdomainRegexp) > 0 and re.search(self.xdomainRegexp,x[2]) :
        return(False)
    return(True)

  #-----------------------------------------------------------------------------------------
  def getHeadOfBlock(self,num) :
    h = f"\n=RequestBlock{num}\n"
    h +='   Num absDelta blkStart   prevReq   start   blocked(ms) realStart  dur(s) initiator page method RC size url\n'
    return(h)

  #-----------------------------------------------------------------------------------------
  def pages(self) :
    with open(self.args.file) as fIn :
      data=json.load(fIn)
    # {'startedDateTime': '2023-01-11T10:13:50.678Z', 'id': 'page_8', 'title': 'https://liv-ssl-vpc-casper.web.travel-ppc.worldline-solutions.com/purchbnpweb/issuer/holder/holderList.xhtml', 'pageCriterias': {'onContentLoad': 1539.8089999798685, 'onLoad': 1539.2819999251515}}i
    if "pages" not in data["log"] :
      return
    pages = data["log"]["pages"]
    print("-------------------- Pages ---------------------------------- ")
    print("Date        hh:mm:ss  page_Id  onContentLoad   onLoad   title ")
    for page in pages :
      date=page['startedDateTime'][0:10]
      hh=page['startedDateTime'][11:-1]
      onContentLoad=float(page['pageTimings']['onContentLoad']) if page['pageTimings']['onContentLoad'] else 0
      onLoad=float(page['pageTimings']['onLoad']) if page['pageTimings']['onLoad'] else 0
      print(f"{date} {hh} {page['id']:10} {onContentLoad:8.3f} {onLoad:8.3f} {page['title'][self.urlBegin:self.urlEnd]}")

  #-----------------------------------------------------------------------------------------
  def showTheResponseContent(self,item) :
    if 'content' in item and item["content"]["size"] > 0 and "text" in item["content"] :
      print(item["content"]["text"])

  #-----------------------------------------------------------------------------------------
  def showTheHeaders(self,item,marker) :
    if "headers" in item :
      headers={}
      for h in item["headers"] :
        headers[h["name"]] = h["value"]
      for n,v in headers.items() :
          print(f' {marker} {n:20s} {v}')
    print()

  #-----------------------------------------------------------------------------------------
  def requests(self) :
    with open(self.args.file) as fIn :
      data=json.load(fIn)
    threshold=int(self.args.threshold) if len(self.args.threshold) > 0 else 5000
    
    absStartm1=0
    blockStart=0
    absDelta=0
    if len(self.range) > 0 :
      entries=Utils().getRealStartSortedEntries(data["log"]["entries"])[self.startIdx:self.endIdx]
    else :
      entries=Utils().getRealStartSortedEntries(data["log"]["entries"])

    blockNum=2
    print(f"-------------------- Requests (total {len(entries)} )--------------- ")
    print(self.getHeadOfBlock(1))
    entriesCount=self.startIdx - 1

    for entry in entries:
      pageref= entry["pageref"] if "pageref" in entry else "--"
      if "request" in entry :
        # _initiator only with edge/chrome
        initiator=entry["_initiator"] if "_initiator" in entry else {"type":"--"}
        logging.debug(f'_initiator {initiator}')
        if type(initiator) is dict and "type" in initiator :
          myType=initiator["type"]
        else :
          myType="--"
        mark="-"
        if myType == "script" or myType=="preflight" :
          mark="+"

        if not self.filterUrlKeep(entry["request"]["url"]) :
          continue
        if not self.filterDomainKeep(entry["request"]["url"]) :
          continue

        criterias={"latency":float(entry["time"])}
        if "size" in entry["response"]["content"] :
          criterias["size"]=entry["response"]["content"]["size"]
        blocked=0
        if "timings" in entry :
          blocked=entry["timings"]["blocked"]
          for timing in entry["timings"] :
            criterias[timing]=entry["timings"][timing]

        if not self.timings.filterCriteriasKeep(criterias) :
          continue

        entriesCount += 1

        # Some calculation of delays
        absStart=Utils().getAbsTime(entry["startedDateTime"])
        realStart=absStart + blocked
        if absStartm1 > 0  :
          delta=absStart - absStartm1
          absDelta=absStart-t0
        else :
          delta=0
          t0=absStart
          blockStart=absStart
        absStartm1=absStart
        if delta > threshold  :
          cr=self.getHeadOfBlock(blockNum)
          blockNum +=1
          blockStart=absStart
        else :
          sinceBlockStart=absStart - blockStart
          cr=""
        sinceBlockStart=absStart - blockStart
        
        # Display
        print(( f'{cr}'
                f' {mark}'
                f' {entriesCount:4}'
                f' {absDelta/1000:8.3f}'
                f' {sinceBlockStart/1000:8.3f}'
                f' {delta/1000:8.3f}' 
                f' {entry["startedDateTime"][11:23]}'
                f' {blocked:8.3f}'
                f' {Utils().getHhmmss(realStart)}'
                f' {float(entry["time"])/1000:6.3f}'
                f' {initiator["type"]:10s}'
                f' {pageref:8s}'
                f' {entry["request"]["method"]:7s}'
                f' {entry["response"]["status"]:3d}'
                f' {entry["response"]["content"]["size"]:8d}'
                f' {self.getIdToDisplay(entry["request"]["url"])}'
        ))
        if self.timing :
          print(f' startedDateTime {entry["startedDateTime"]}')
          print(f' time {entry["time"]}')
          print(f' timing :  {json.dumps(timing,indent=2)}')
        if self.showHeaders :
          self.showTheHeaders(entry["request"],'* ')
          self.showTheHeaders(entry["response"],'**')
        if self.showResponseContent :
          self.showTheResponseContent(entry["response"])
        if self.hardisplay :
          if "content" in entry["response"] and "text" in entry["response"]["content"] and self.textTrunc > 0 :
            entry["response"]["content"]["text"]=entry["response"]["content"]["text"][0:self.textTrunc] + "......"
          print(json.dumps(entry,indent=4))
 
