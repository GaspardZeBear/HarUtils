import logging

class Utils() :

  def __init__(self) :
    pass

  def getHhmmss(self,t) :
    seconds=t//1000
    milliseconds=t - 1000*seconds
    hh=seconds//3600
    mm=(seconds-hh*3600)//60
    ss=seconds-hh*3600 -mm*60
    return(f"{hh:2.0f}:{mm:2.0f}:{ss:2.0f}.{milliseconds:03.0f}")


  def getAbsTime(self,t) :
    hh=int(t[11:13])
    mm=int(t[14:16])
    ss=int(t[17:19])
    ms=int(t[20:23])
    absStart=1000*(hh*3600 + mm*60 + ss) + ms
    #print(f'{t} {hh} {mm} {ss} {ms} {absStart}')
    return(absStart)

  def getRealStartSortedEntries(self,entries) :
    entriesDict={}
    for entry in entries:
      if "request" in entry :
        start=entry["startedDateTime"]
        absStart=self.getAbsTime(start)
        blocked=0
        if "timings" in entry : 
          if "blocked" in entry["timings"] : 
            blocked=entry["timings"]["blocked"]
        realStart=self.getAbsTime(start) + blocked
        if realStart not in entriesDict :
          entriesDict[realStart]=entry
        else :
          fakeStart = realStart
          while fakeStart in entriesDict :
            logging.info(f"Duplicate time {fakeStart}, adding 0.001 for url {entry['request']['url']} ")
            fakeStart += 0.001
          entriesDict[fakeStart]=entry
    myKeys = list(entriesDict.keys())
    myKeys.sort()
    sortedEntries = [entriesDict[i] for i in myKeys]
    return(sortedEntries)


