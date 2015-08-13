#! /usr/bin/python

import jsonrpc
import sys, os
import math
from sys import argv

# 'fee' is a 2d list: [NBT,NSR]
fee=[0.01,1]
#'startblk' and 'endblk' are the start and end for the simulation
starblk=1
endblk=481288
#'space' is how often the simulation outputs a datapoint
space=100

#I don't remember why I did it this way, just leave 'c' alone unless you know what's up
c=starblk

#Configure RPC
#NUCONFIG='%s/.nu/nu.conf'%os.getenv("HOME")
#If you are windows, comment you the previous line and uncomment the following:
NUCONFIG=r'%s\nu\nu.conf'%os.getenv("APPDATA")
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

t=0
blocktxfee=[0,0]
totaltxfee=[0,0]
for w in range(starblk,endblk):
 blk=rpc.getblock(rpc.getblockhash(w))
 txns=blk['tx']
 for txid in txns:
  amountout=0
  amountin=0
  tx=rpc.decoderawtransaction(rpc.getrawtransaction(txid))
  vouts=[]
  for j in tx['vout']:
   amount=0
   amount=j['value']
   if amount>0:
    amountout+=amount
  for j in tx['vin']:
   try:
    intx=rpc.decoderawtransaction(rpc.getrawtransaction(j['txid']))
    amountin+=intx['vout'][j['vout']]['value']
   except:
    coinbase=True
  if coinbase==False:
   txfee=amountin-amountout
   if txfee<0:
    txfee=0
  else:
   txfee=0
   coinbase=False
  if tx['vout'][0]['scriptPubKey']['type']=='pubkeyhash':
   nbt=tx['vout'][0]['scriptPubKey']['addresses'][0].startswith("B")
   nsr=tx['vout'][0]['scriptPubKey']['addresses'][0].startswith("S")
  else:
   nbt=False
   nsr=False
  if coinbase==False and nbt:
   blocktxfee[0]+=txfee*fee[0]/0.01
   txfee=0
  if coinbase==False and nsr:
   blocktxfee[1]+=txfee*fee[1]
   txfee=0
 totaltxfee[0]+=blocktxfee[0]
 totaltxfee[1]+=blocktxfee[1]
 blocktxfee=[0,0]

 t+=1
 if t==space:
  c+=space
  with open("variablefees.txt", "a") as myfile:
    myfile.write(str(c)+' '+str(totaltxfee[0])+' '+str(totaltxfee[1])+' '+str(blocktxfee[0])+' '+str(blocktxfee[1])+"\n")
  t=0
