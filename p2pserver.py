import socket
from os import popen
from struct import *
from time import time, sleep
import sys
import types
import string
import random
import pickle

ENDC = '\033[0m'
OKGREEN = '\033[92m'
OKRED = '\033[91m'

class pServerWorker:

    sessionstruct = {
        'id': '',
        'address': '',
        'port': 0,
        'sent_ka': 0,
        'recv_ka': 0
    }

    def __init__(s, server, port, myid):
        s.client = s.sessionstruct 

        s.server = server
        s.srvport = port
        s.myid = myid
        s.conn_to = '' 
        s.wait_client = ''
        s.debug = False
        
        s.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.socket.connect((server,port))

        s.srcip = s.socket.getsockname()[0]
        s.srcport = s.socket.getsockname()[1]
        s.socket.close()

        s.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.socket.setblocking(0)
        s.socket.bind((s.srcip, s.srcport))
        s.logger(s.myid + " listening on " + s.srcip + ":" + str(s.srcport) + "\n")
        s.bufflen = 65535 


    def sig_exit_handler(s):
        sys.exit(0)

    def logger(s, data):
        if s.debug:
            sys.stderr.write(OKGREEN + data + ENDC)

    def send_data(s, addr='', port=0, data=''):
        if not addr:
            addr=s.server

        if not port:
            port=s.srvport

        while True:
            try:
                s.socket.sendto(data, (addr, port))
                s.logger("UDP: sent  " + str(len(data)) + " " + data + " \n")
                break
            except IOError, e:
                if e.errno == 11: 
                    s.logger("UDP socket busy")
                    sleep(0.01)

    def send_packet_data(s, addr, port, cmdid, data):
        uniqstr = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(4))
        pdata = pack("H4sI%ds" % (len(data)), cmdid, uniqstr, len(data), data)
        s.send_data(addr, port, pdata)

    def recv_data(s):
        response, addrport = s.socket.recvfrom(s.bufflen)

        s.logger("UDP: received  " + str(len(response)) + " bytes " + response + "\n")
        
        if addrport[0] == s.server and addrport[1] == s.srvport:
            s.pCmdHandler(response)
            
        else:
            (cmdid, uniqstr, psize) = unpack("H4sI", response[:12])
            pdata = response[12:12+psize]
            s.catch_client_cmd(addrport, cmdid, psize, pdata)

    def register(s):
        s.send_data(data = "set " + s.myid)
        
    def connect_to(s, uid):
        s.conn_to = uid
        s.logger("Connect to client " + s.conn_to + "\n")

    def wait_for(s, uid):
        s.wait_client = uid
        s.logger("Wait client " + s.wait_client + "\n")
    
    def pCmdHandler(s, data):
        r = str(data).strip(">").rstrip().split(" ")

        if r[0] == s.myid and r[1] == 'registered':
            s.logger("Registered on server\n")

            if s.conn_to > '':
                s.logger("Connecting to " + s.conn_to + "\n")
                s.send_data(data = "get " + s.conn_to)
                s.send_data(data = "conn " + s.conn_to)

            if s.wait_client > '' and s.client['address'] > '' and s.client['port'] > 0: 
                s.send_packet_data(s.client['address'], int(s.client['port']), 0, data=s.myid)
                s.client['sent_ka'] += 1

            if len(r) > 2:
                s.logger("Daemon: Query to connect from " + r[2] + "\n")
                claddr, clport = r[2].split(":")
                s.send_packet_data(claddr, int(clport), 0, data=s.myid)
                s.client['sent_ka'] += 1
                s.client['address'] = claddr
                s.client['port'] = clport

        elif r[0] == 'client':
            claddr, clport = r[2].split(":")
            s.client['id'] = r[1]
            s.send_packet_data(claddr, int(clport), 0, data=s.myid)
            s.client['sent_ka'] += 1
            s.client['address'] = claddr
            s.client['port'] = clport

            s.logger("Daemon: added client " + r[2] + " as " + r[1] + "\n")


    def catch_client_cmd(s, addrport, cmdid, size, response):
        r = str(response)
        s.logger("Cmd received " + r + "\n")

        if s.client['address'] == addrport[0] and int(s.client['port']) == addrport[1]:
            if cmdid == 0:
                s.logger("Got KA from " + response + "\n")

                if s.client['id'] == '' and s.wait_client == response:
                    s.client['id'] = response
                        
                if (s.wait_client == response or s.conn_to == response) and s.client['id'] == response:
                    s.send_packet_data(addrport[0], addrport[1], 0, data=s.myid)
                    s.client['recv_ka'] += 1
                    s.client['sent_ka'] += 1

                    if s.client['recv_ka'] > 1 and s.wait_client != '':
                        print "# client id\tyour addr\tyour local port"
                        print s.client['id'] + "\t" +  s.srcip + "\t" +  str(s.srcport)
                        sys.exit(0)

                    if s.client['sent_ka'] > 2 and s.conn_to != '':
                        print "# client id\tclient addr\tclient port\tyour local port"
                        print s.client['id'] + "\t" +  s.client['address'] + "\t" + str(s.client['port']) + "\t" + str(s.srcport)
                        sys.exit(0)
 




