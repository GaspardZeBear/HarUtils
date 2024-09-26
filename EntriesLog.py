import logging
#-----------------------------------------------------
class EntriesLog() :
  def __init__(self) :
    self.log=[]

  #-----------------------------------------------------
  def logEntry(self,stats,idx,entry) :
    self.log.append({
        'idx' : idx+1,
        'stats' : stats,
        'entry' : entry
        })
  #-----------------------------------------------------
  def printAll(self) :
    for l in self.log :
      if not "pageref" in l['entry'] :
        l['entry']["pageref"]=None
      print('*'*128)
      print("Request num : {}/{} pageref {} kept {} discarded {} ".format(
          l['idx'],
          l['stats']['total'],
          l['entry']["pageref"],
          l['stats']['kept'],
          l['stats']['discarded']
          ))
      print('-'*128)
      print("{} {}\n{}".format(
        l['entry']["request"]["method"],
        l['entry']["request"]["url"],
        l['entry']["request"]["queryString"],
      ))
      print('-'*128)
      print(l['entry']["request"])
      print('-'*128)
      print(" {} {}".format(
        l['entry']["response"]["status"],
        l['entry']["response"]["statusText"],
      ))
      print()


