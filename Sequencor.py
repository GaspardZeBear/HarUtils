import logging
import threading
import time

#-----------------------------------------------------
class Sequencor() :
  useLocks=None
  locks=[]
  lockValues=[]
  sleeping=0.001

  @staticmethod
  def activate() :
    Sequencor.useLocks=True

  @staticmethod
  def inactivate() :
    Sequencor.useLocks=False

  @staticmethod
  def isActive() :
    return(Sequencor.useLocks)

  @staticmethod
  def addLock(hold=True) :
    Sequencor.locks.append(threading.Lock())
    with Sequencor.locks[len(Sequencor.locks) -1 ] :
      Sequencor.lockValues.append(hold)

  @staticmethod
  def freeLock(idx) :
    with Sequencor.locks[idx] :
      Sequencor.lockValues[idx] = False


  @staticmethod
  def waitGo(idx) :
    go = False
    if Sequencor.useLocks and idx > 0 :
      while go == False :
        with Sequencor.locks[idx-1] :
          if Sequencor.lockValues[idx-1] == 0 :
            go = True
          else :
            logging.warning(f'nogo for wake up of idx {idx}')
        time.sleep(Sequencor.sleeping)

