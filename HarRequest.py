import json
import re
import logging
import requests
import time
import datetime
import threading
from HarResponseProvider import *
from Sequencor import *


#---------------------------------------------------------------------------------------
class HarRequest() :

  #---------------------------------------------------------------------------------------
  def __init__(self,idx,delay) :
    self.idx=idx
    logging.info(f'HarRequest idx {idx} starting will sleep {delay} ')
    time.sleep(delay)
    logging.info(f'HarRequest idx {idx} waking up after {delay} ')
    if Sequencor.isActive() : 
      Sequencor.waitGo(idx)
      Sequencor.freeLock(idx)
    logging.info(f'HarRequest idx {idx} running {delay} ')
    self.entry=HarResponseProvider.getFragments()[idx]
    self.play()

  #---------------------------------------------------------------------------------------
  def getHeaders(self) :
    headers={"HarIdx":str(self.idx)}
    for h in self.entry["request"]["headers"] :
      if not h["name"].startswith(":") :
        headers[h["name"]]=h["value"]
    return(headers)

  #---------------------------------------------------------------------------------------
  def doGet(self) :
    logging.info(f'Request {self.idx} GET {self.entry["request"]["url"]}')
    r=requests.get(self.entry["request"]["url"],
            params={
            'query': None
            },
            headers=self.getHeaders(),
            allow_redirects=False,
            verify=False)
    resp=r.text[0:80]
    resp=r.text
    logging.info(f'Request {self.idx} GET code={r.status_code} ok={r.ok} ')
    #logging.info(f'{resp}')


  #---------------------------------------------------------------------------------------
  def doOptions(self) :
    logging.info(f'Request {self.idx} OPTIONS {self.entry["request"]["url"]}')
    r=requests.options(self.entry["request"]["url"],
            params={
            'query': None
            },
            headers=self.getHeaders(),
            allow_redirects=False,
            verify=False)
    resp=r.text[0:80]
    resp=r.text
    logging.info(f'Request {self.idx} OPTIONS code={r.status_code} ok={r.ok} ')
    #logging.info(f'{resp}')

  #---------------------------------------------------------------------------------------
  def doPut(self) :
    logging.info(f'Request {self.idx} PUT {self.entry["request"]["url"]}')
    r=requests.put(self.entry["request"]["url"],
            params={
            'query': None
            },
            headers=self.getHeaders(),
            allow_redirects=False,
            verify=False)
    resp=r.text[0:80]
    resp=r.text
    logging.info(f'Request {self.idx} PUT code={r.status_code} ok={r.ok} ')
    #logging.info(f'{resp}')





  #---------------------------------------------------------------------------------------
  def doPost(self) :
    logging.info(f'Request {self.idx} POST {self.entry["request"]["url"]}')
    params={}
    for p in self.entry["request"]["postData"]["params"] :
      if not p["name"].startswith(":") :
        params[p["name"]]=p["value"]
      r=requests.get(self.entry["request"]["url"],
           params=params,
           data=self.entry["request"]["postData"]["text"],
           headers=self.getHeaders(),
            allow_redirects=False,
           verify=False)
    resp=r.text[0:80]
    resp=r.text
    logging.info(f'Request {self.idx} POST code={r.status_code} ok={r.ok} ')
  #---------------------------------------------------------------------------------------


  def play(self) :
    #HarResponseProvider.setHarFragment(entry)
    #logging.info('-'*128)
    logging.info(f'Request idx {self.idx} {self.entry["request"]["method"]} {self.entry["request"]["url"]} starting')
    headers={}
    for h in self.entry["request"]["headers"] :
      if not h["name"].startswith(":") :
        headers[h["name"]]=h["value"]
    try :
      if self.entry["request"]["method"] == "GET" :
        self.doGet()
      elif self.entry["request"]["method"] == "POST" :
        self.doPost()
      elif self.entry["request"]["method"] == "OPTIONS" :
        self.doOptions()
      elif self.entry["request"]["method"] == "PUT" :
        self.doPut()
      else :
        raise Exception(f'Unsupported method {self.entry["request"]["method"]}')
    except Exception as e :
      logging.warning(f'Exception {e}')
      pass
    print(f'Request idx {self.idx} done')

  #---------------------------------------------------------------------------------------

  def Xplay(self) :
    for idx,entry in enumerate(self.data["log"]["entries"]) :
      HarResponseProvider.setHarFragment(entry)
      logging.info('-'*128)
      logging.info(f'Request {idx} {entry["request"]["method"]} {entry["request"]["url"]}')
      headers={}
      for h in entry["request"]["headers"] :
        if not h["name"].startswith(":") :
          headers[h["name"]]=h["value"]
      try :
        if entry["request"]["method"] == "GET" :
          self.doGet(entry)
        elif entry["request"]["method"] == "POST" :
          self.doPost(entry)
        else :
          raise Exception(f'Unsupported method {entry["request"]["method"]}')
      except Exception as e : 
        logging.warning(f'Exception {e}')
        pass
    print("Hit CTRL-C to finish")

