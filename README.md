# What is it

This script demonstrates how to connect using UDP hole punching.

# How it works

This script is a part of p2p service that uses UDP to connect to other clients.

Script requires server udphelper.lua runned on somewhere in internet.
Server helps clients to find each other by sending them its real ip addressed and ports.
Then clients need to use UDP Hole Punching method to connect.

udphepler.lua must runs on server with real IP but clients do not require it and
can run behind firewall with NAT.

# Usage

usage: p2ptool.py [-h] [--myid MYID] [-p P] [--connect CONNECT] [--wait WAIT]
                  [-v]
                  server

 positional arguments:
   server             helper server ip
 
 optional arguments:
   -h, --help         show this help message and exit
   --myid id          id to find you
   -p Port            server port
   --connect id       auto connect to
   --wait id          wait client and exit
   -v                 verbose mode

On first client

 ./p2ptool.py --myid first-client-id -p 8001 --connect second-client-id helper-server-ip

On second client

 ./p2ptool.py --myid second-client-id -p 8001 --wait first-client-id helper-server-ip

When UDP hole was panched all client will finish:
- first client will return: id, client address, client port, your src port
- second client will return: id, own local address, own src port

Then you can use any other software that uses udp exchange.



