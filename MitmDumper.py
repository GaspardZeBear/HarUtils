from mitmproxy import proxy, options
from mitmproxy.tools.dump import DumpMaster
from mitmproxy.addons import core
from mitmproxy.tools.main import mitmdump
class MitmDumper() :
 
  def __init__(self,args):
    #mitmdump(args=["-s", "HarReplayFromProxy.py")
    mitmdump(args=["-s", "HarReplayFromProxy.py","--listen-port",args.mitmproxyport])
    print("mitmdump Started")


