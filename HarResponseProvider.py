class HarResponseProvider :

  fragments=[]
  fragment=None
  counter=-1

  def __init__(self) :
    pass

  @staticmethod
  def setHarFragment(fragment) :
    HarResponseProvider.fragment=fragment
    HarResponseProvider.counter += 1

  @staticmethod
  def getHarFragment() :
    return(HarResponseProvider.fragment)

  @staticmethod
  def appendFragments(fragment) :
    HarResponseProvider.fragments.append(fragment)

  @staticmethod
  def getFragments() :
    return(HarResponseProvider.fragments)

  @staticmethod
  def getCounter() :
    return(HarResponseProvider.counter)
