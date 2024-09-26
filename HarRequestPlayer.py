import json
import re
import logging
import requests
import time
import datetime
import threading
from HarResponseProvider import *
from HarRequest import *
from Sequencor import *
from Utils import *


#------------------------------------------------------------------------------------------
# These lines enable debugging at httplib level (requests->urllib3->http.client)
# You will see the REQUEST, including HEADERS and DATA, and RESPONSE with HEADERS but without DATA.
# The only thing missing will be the response.body which is not logged.
#try:
#    import http.client as http_client
#except ImportError:
# Python 2
#    import httplib as http_client
#http_client.HTTPConnection.debuglevel = 1
#------------------------------------------------------------------------------------------

#-----------------------------------------------------
class HarRequestPlayer() :

  def __init__(self, args) :
    self.args=args
    self.range=args.range
    self.startIdx=0
    self.endIdx=0
    if len(self.range) > 0 :
      t=self.range.split(",")
      self.startIdx=int(t[0])
      self.endIdx=int(t[1])

    self.harFile=args.file
    initialDelay=int(args.setuptime)
    Sequencor.activate()
    if args.inactivate :
      Sequencor.inactivate()
    self.data=None
    with open(self.harFile) as f:
      self.data = json.load(f)

    if len(self.range) > 0 :
        entries=Utils().getRealStartSortedEntries(self.data["log"]["entries"])[self.startIdx:self.endIdx]
    else :
      entries=Utils().getRealStartSortedEntries(self.data["log"]["entries"])

    #for idx,entry in enumerate(self.data["log"]["entries"]) :
    for idx,entry in enumerate(entries) :
      HarResponseProvider.appendFragments(entry)
      print(f'{idx} {entry["startedDateTime"]} {entry["request"]["url"]}')

    if not args.threading :
      Sequencor.inactivate()
      logging.info(f'HarRequestPlayer will wait {initialDelay} seconds to ensure mitmproxy really started')
      time.sleep(initialDelay)
      #for idx,entry in enumerate(self.data["log"]["entries"]) :
      for idx,entry in enumerate(entries) :
        HarRequest(idx,0)
      return 
    # If threading
    self.beat=[]
    #for idx,entry in enumerate(self.data["log"]["entries"]) :
    for idx,entry in enumerate(entries) :
      dt = datetime.datetime.strptime(entry["startedDateTime"], '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%s')
      t=entry["startedDateTime"]
      hh=1000*3600*int(t[11:13])
      mm=1000*60*int(t[14:16])
      ss=1000*int(t[17:19])
      ms=int(t[20:23])
      dt=hh+mm+ss+ms
      #print(f'{idx} {hh}:{mm}:{ss}.{ms} {dt} {entry["startedDateTime"]} {ms} {entry["request"]["url"]}')
      self.beat.append(dt)
      #HarResponseProvider.appendFragments(entry)
      # 2022-12-19T17:39:52.720Z

    # create the beat (time when threads will really begin to work
    # add step to ensure right sequence
    # shorten if too much time between request
    initialBeat=self.beat.copy()
    step=int(args.step)
    shorten=int(args.shorten)
    t0=self.beat[0]
    for idx,beat in enumerate(self.beat) :
      self.beat[idx] = beat - t0
    for idx,beat in enumerate(self.beat) :
      if idx > 0 :
        if self.beat[idx] - self.beat[idx-1] < step :
          logging.debug(f'Adding step {step} to {self.beat[idx]}')
          self.beat[idx] = self.beat[idx-1] + step
        if shorten > 0 :
          beatIdx=self.beat[idx]
          if self.beat[idx] - self.beat[idx-1] > shorten :
            self.beat[idx] = self.beat[idx-1] + shorten
            for i in range(idx+1, len(self.beat)) :
              self.beat[i] -= beatIdx

    for idx,beat in enumerate(self.beat) :
      logging.info(f'beat idx {idx}  initial {initialBeat[idx]} fixed {idx} {beat}')

    initialDelay=int(args.setuptime)
    logging.info(f'HarRequestPlayer will wait {initialDelay} seconds to ensure mitmproxy really started')
    time.sleep(initialDelay)
    logging.info(f'HarRequest go')
    millisec0 = time.time_ns() // 1000000
    print(millisec0)

    for idx,entry in enumerate(HarResponseProvider.getFragments()) :
      logging.info(f'Starting thread for {idx} delay {self.beat[idx]}')
      Sequencor.addLock()
      threading.Thread(target=self.startHarRequest, args=(self.beat[idx]/1000,idx)).start()

    pass

  #---------------------------------------------------------------------------------------
  def startHarRequest(self,delay,idx):
    logging.info(f'start idx {idx} delay {delay}')
    HarRequest(idx,delay)
    logging.info(f'idx {idx} delay {delay} done')

