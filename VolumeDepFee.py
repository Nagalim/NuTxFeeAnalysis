#! /usr/bin/python

import jsonrpc
import sys, os
import math
from sys import argv

# 'p' is the fee multiplier
p=1
#'startblk' and 'endblk' are the start and end for the simulation
starblk=1
endblk=407231
#'space' is how often the simulation outputs a datapoint
space=100

#I don't remember why I did it this way, just leave 'c' alone unless you know what's up
c=starblk

#Configure RPC
NUCONFIG='%s/.nu/nu.conf'%os.getenv("HOME")
#If you are windows, comment you the previous line and uncomment the following:
#NUCONFIG=r'%s\nu\nu.conf'%os.getenv("APPDATA")
opts = dict(tuple(line.strip().replace(' ','').split('=')) for line in open(NUCONFIG).readlines())
try:
  rpc = jsonrpc.ServiceProxy("http://%s:%s@127.0.0.1:%s"%(
    opts['rpcuser'],opts['rpcpassword'],opts.pop('rpcport', 14002)))
except:
  print "could not connect to nbt daemon"
  sys.exit(1)
try:
  nsrrpc = jsonrpc.ServiceProxy("http://%s:%s@127.0.0.1:%s"%(
    opts['rpcuser'],opts['rpcpassword'],opts.pop('rpcport', 14001)))
except:
  print "could not connect to nsr daemon"
  sys.exit(1)
try:
  blkcnt = rpc.getblockcount()
except:
  print "Issues with RPC"
  sys.exit(1)

switch=0
t=0
totgain=0
for w in range(starblk,endblk):
 blktax=0
 blk=rpc.getblock(rpc.getblockhash(w))
 txns=blk['tx']
 for txid in txns:
  tx=rpc.decoderawtransaction(rpc.getrawtransaction(txid))
  vouts=[]
  for j in tx['vout']:
   amount=0
   amount=j['value']
   if amount>0:
    try:
     addy=j['scriptPubKey']['addresses']
     if addy[0].startswith("B"):
      if len(tx['vin'])==1:
       if tx['vin'][0]['txid']!='0000000000000000000000000000000000000000000000000000000000000000':
        try:
         intx=rpc.decoderawtransaction(rpc.getrawtransaction(tx['vin'][0]['txid']))
         inaddy=intx['vout'][0]['scriptPubKey']['addresses']
        except:
         inaddy=['coinbase']
        if inaddy[0]==addy[0]:
         switch=1
        else:
         vouts.append(amount)
      else:
       vouts.append(amount)
    except:
     stall=0
  if len(vouts)>1:
   if switch==0:
    vouts.remove(max(vouts))
   else:
    switch=0
  if len(vouts)>0:
   tax=-0.01
   for q in vouts:
    if q>1:
     tax+=p*max(0.01,q/(100+100*math.log(q,10)))
    else:
     tax+=p*0.01
   blktax+=tax
 totgain+=blktax
 t+=1
 if t==space:
  c+=space
  with open("fees.txt", "a") as myfile:
    myfile.write(str(c)+' '+str(totgain)+"\n")
  t=0
