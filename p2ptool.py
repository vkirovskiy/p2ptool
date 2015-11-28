#!/usr/bin/env python
# UDP hole punching
# client-1 (192.168.1.1 srcport 1234) -> (register, conn cmd to client-2) -> server (192.168.2.1 dstport 8001)
# server store real ip and srcport client-1 (192.168.1.1:1234)
# client-2 (192.168.3.1 srcport 4567) -> (register cmd ) -> server (192.168.2.1 dstport 8001)
# server response -> (client-1 is 192.168.1.1:1234) -> client-2

import select
import socket
import sys
from time import time
import argparse
from p2pserver import pServerWorker
import signal

parser = argparse.ArgumentParser()
parser.add_argument("--myid", help="id to find you")
parser.add_argument("-p", type=int, help="server port")
parser.add_argument("server", help="helper server ip")
parser.add_argument("--connect", help="auto connect to")
parser.add_argument("--wait", help="wait client and exit")
parser.add_argument("-v", action='store_true', help="verbose mode")

args = parser.parse_args()
if args.myid:
    myid = args.myid

if args.server:
    SERVER=args.server
    if args.p:
        SRVPORT=args.p
    else:
        SRVPORT=8001

pworker = pServerWorker(SERVER, SRVPORT, myid)

def sig_exit(sig, f):
    pworker.sig_exit_handler()
    sys.exit(0)

if args.l: pworker.packetlog = args.l
if args.wait: pworker.wait_for(args.wait)
if args.connect: pworker.connect_to(args.connect)
if args.v: pworker.debug = True

signal.signal(signal.SIGINT, sig_exit)

pworker.register()
t1 = time()

socks = [pworker.socket]

while True:
    r, w, e = select.select(socks,[],[],10)

    for s in r:
        if s == pworker.socket:
            pworker.recv_data()
        else:
            print "Unknown socket"

    t2 = time()
    if t2-t1>5: 
        pworker.register()
        t1=t2

