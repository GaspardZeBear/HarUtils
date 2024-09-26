# hartools

Some tools to use .har (http archive recording) 

## Har.py 

Entry point for some actions

### hints 

Sometimes har is not well ordered.
Notably, OPTIONS are timestamped after GET but in reality it is sent before !
When adding blocked time to start time, all seems to go in correct order, so we did it.
So Display order may not correspond to real har order.

### filter : generate an har file without urls corresponding to some unwanted patterns (ex : gif, png, css)  

### replay : replays the requests from an har file

export PYTHONWARNINGS="ignore:Unverified HTTPS request"

Integrate mitm certif in cacerts for JMeter recorder

- root@WL-F5NQFB3:~# cd /home/docker/.mitmproxy/
- root@WL-F5NQFB3:/home/docker/.mitmproxy#  keytool -import -alias mitmproxy -file mitmproxy-ca-cert.pem -cacerts

start mitmproxy mode upstream to chain proxies

mitmweb --mode upstream:https://nextproxy:8080 --web-port 1930 --listen-port 1931 -k


Sample with JMeter recorder :
- First time, have JMeter trust mitmproxy certificate 
- Start jmeter recorder on port 8888 using mitm response player as proxy : ./jmeter -H localhost -P 8080
  All requests will be sent to mitm responder
- Start har player :  https_proxy=http://localhost:8888 python3 Har.py -vv replay  --file simple.petstore.octoperf.com.har 
  This will start embedded mitm responder on localhost port 8080
  Requests will be sent to JMeter recorder and received by mitm responder
- Then save recording and replay it without proxy : ./jmeter

https_proxy=http://localhost:8090 PYTHONWARNINGS="ignore:Unverified HTTPS request" python3 Har.py replay  --shorten 5000 --step 10 --file qlf-ch-energie-public-asp2.svc.meshcore.net-chrome-20221128.har
https_proxy=http://localhost:8099 PYTHONWARNINGS="ignore:Unverified HTTPS request" python3 Har.py replay -m 8099  --shorten 5000 --step 10 --file qlf-ch-energie-public-asp2.svc.meshcore.net-chrome-20221128.har


### Replay, technical notes

Replay embeds mitmdump with a response player (HarReplayFromProxy.py) : mitmdump must be the main thread (error if not done like this !)
Then it starts a specific HarRequestPlayer (HarRequestPlayer.py) thread.

Threads share a common structure, HarResponseProvider.py

At start, HarRequestPlayer fills HarResponseProvider with extracts from har file :
- an extract = 1 har entry, that contains request and response
- share is a list, each fragment has a rank in the list (idx)

Then HarRequestPlayer start a thread HarRequest foreach request in the har.
Each thread will really work after a delay computed from the har.
Each thread knows its idx, so it can pick infos from the request in shared structure : it can build request (headers params etc ...)
The idx is sent as a Header in the request, "HarIdx"

When receiving the request, HarReplayFromProxy picks up the idx from headers, and picks up the response infos from HarResponseProvider  (headers ...)

Note on thread dispatching and sleeping

Real dispatching of thread may not be precise and order can change if sleep < 10ms (roughly).
Sequencor forces request to start in real order, not "randomly" : option -i inactivates sequencor
If 2 requests have the same start timestamp, it may be interesting to add an offset to the second one : parameter step. 
mitmproxy should process in the right order (not true is step too low)

Do the most reproducable replay is gotten with sequencor and step > 10 ms ...
But this may produce an a bit biased scenario.

Note : mitmproxy cannot reproduce response time : introducing time.sleep entirely pauses mitmproxy :(

## JtlFilter.py : filter JTL file

### filter : filter JTL file

Filter JTL file according to criterias. By default regexp on URL field.

Filtering can be :
- inclusive : only include patterns : default pattern file is provided with some current filter 
- exclusive : exclude patterns 

Timestamp col may be converted to and from epoch :
- enhance readability
- enhance filtering by timestamp


### label  :  extract urls associated to labels 


### merge  :  adds url in label field (more readable report)



## Explore.py : deprecated, integrated in Har.py

- analyze an HAR file : show the request and their chronology, tries to group them by idle delay

## Sequencor.py : a simple module to guarantee the starting order of threads

According to machine load, thread starting with an interval between 0-10ms won't be launced in the expected order.

Sequencor ensure that thread with index i won't operate before i-1 has begun to work.

## Description


## Installation
 
python

## Usage

## jq !!

 cat test_liv-ssl-vpc-casper.web.travel-ppc.worldline-solutions.com.har | jq -r '.log.entries[] | [.startedDateTime,.request.url]|@csv'
 cat test_liv-ssl-vpc-casper.web.travel-ppc.worldline-solutions.com.har | jq -r '.log.entries[] | [.startedDateTime[:-1],.time,.request.url[65:]]|@csv' | sort -t ',' -k2 -n

