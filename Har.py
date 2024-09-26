import json
import re
import logging
import argparse
import threading
from Filterer import *
from Explorer import *
from HarRequestPlayer import *
from HarResponseProvider import *
from MitmDumper import *

#-----------------------------------------------------
def playerThread(args) :
  #harPlayer=HarRequest(args.file).play()
  harPlayer=HarRequestPlayer(args)

#-----------------------------------------------------
def fReplay(args) :
  threading.Thread(target=playerThread, args=(args,)).start()
  #mitmdump(args=["-s", "HarReplayFromProxy.py"])
  MitmDumper(args)
  #print("mitmdump Started")

#-----------------------------------------------------
def fFilter(args) :
  Filterer(args)

#-----------------------------------------------------
def fExplore(args) :
  Explorer(args)

#----------------------------------------------------------------
parser = argparse.ArgumentParser()

subparsers = parser.add_subparsers(help='sub-command help')
parser.add_argument('-v', '--verbose',
                    action='count',
                    dest='verbose',
                    default=0,
                    help="verbose output (repeat for increased verbosity)")

parserFilter = subparsers.add_parser('filter', help='a help')
parserFilter.set_defaults(func=fFilter)
#parserFilter.add_argument('--alert','-a',default=False,action='store_true',help="Send alert")
parserFilter.add_argument('--file','-f',default="",help="har file to process")
parserFilter.add_argument('--out','-o',default="",help="Generated har")
parserFilter.add_argument('--exclude','-x',default="HarExclude.json",help="Exclude url pattern file '' to skip")
parserFilter.add_argument('--mexclude','-m',default="",help="manual exclude patterns comma")

parserReplay = subparsers.add_parser('replay', help='a help')
parserReplay.set_defaults(func=fReplay)
parserReplay.add_argument('--file','-f',default="",help="har file to process")
#parserReplay.add_argument('--proxy','-p',default="",help="proxy")
parserReplay.add_argument('--step','-s',default="2",help="millisecond step to shift request starting if 2 start together")
parserReplay.add_argument('--mitmproxyport','-m',default="8090",help="mitmproxy port")
parserReplay.add_argument('--offset','-o',default="2",help="millisecond initial interval betwen threads")
parserReplay.add_argument('--setuptime','-t',default="20",help="second delay to ensure all started right")
parserReplay.add_argument('--inactivate','-i',default=False,action='store_true',help="inactive sequencor")
parserReplay.add_argument('--threading','-x',default=True,action='store_false',help="threading off")
parserReplay.add_argument('--shorten',default="0",help="Shorten interval between request to value in milliseconds")
parserReplay.add_argument('--range','-r',default="",help="range")
parserReplay.add_argument('--first',default="0",help="first request to play")
parserReplay.add_argument('--last',default="0",help="last request to play")

parserExplore = subparsers.add_parser('explore', help='')
parserExplore.set_defaults(func=fExplore)
parserExplore.add_argument('--file','-f',default="",help="har file to process")
parserExplore.add_argument('--threshold','-t',default="5000",help="Milliseconds Time elapsed to consider new block")
parserExplore.add_argument('--hardisplay',default=False,action='store_true',help="Display har entry")
parserExplore.add_argument('--showHeaders',default=False,action='store_true',help="Show headers")
parserExplore.add_argument('--showResponseContent',default=False,action='store_true',help="Show response content")
parserExplore.add_argument('--idomain',default=".*",help="filter include domain")
parserExplore.add_argument('--xdomain',default="",help="filter exclude domain")
parserExplore.add_argument('--minclude','-i',default=".*",help="filter include regexp")
parserExplore.add_argument('--mexclude','-x',default="",help="filter exclude regexp")
parserExplore.add_argument('--dns',default="0",help="show only dns timing greater than ")
parserExplore.add_argument('--connect',default="0",help="show only connect timing greater than ")
parserExplore.add_argument('--ssl',default="0",help="show only ssl timing greater than ")
parserExplore.add_argument('--blocked',default="0",help="show only blocked timing greater than ")
parserExplore.add_argument('--wait',default="0",help="show only wait timing greater than (network latency)")
parserExplore.add_argument('--receive',default="0",help="show only receive timing greater than (long size ?)")
parserExplore.add_argument('--send',default="0",help="show only send timing greater than (long size ?)")
parserExplore.add_argument('--latency',default="0",help="show only total latency greater than ")
parserExplore.add_argument('--range','-r',default="",help="range")
parserExplore.add_argument('--name',default=False,action='store_true',help="Display only url last part")
parserExplore.add_argument('--timing',default=False,action='store_true',help="Display timing")
parserExplore.add_argument('--urlBegin','-b',default="0",help="Display url 1rst pos")
parserExplore.add_argument('--urlEnd','-e',default="120",help="Display url last pos")


args=parser.parse_args()
loglevels=[logging.ERROR,logging.WARNING,logging.INFO,logging.DEBUG,1]
loglevel=loglevels[args.verbose] if args.verbose < len(loglevels) else loglevels[len(loglevels) - 1]
logging.basicConfig(stream=sys.stdout,format="%(asctime)s %(module)s %(name)s  %(funcName)s %(lineno)s %(levelname)s %(message)s", level=loglevel)
logging.log(1,'Deep debug')
args.func(args)

