from socket import *
import os
import sys
import struct
import time
import select
import binascii
import socket
#import antigravity
#import raw_input

def getDestination():
    return raw_input("What address should we ping?")

notDone=True
while notDone:
    method=raw_input("To ping a server type 'ping' or to traceroute a server type 'trace' \n")
    if method=="trace":
        destination=getDestination()
        os.system("python Traceroute.py ", destination)
        notDone=false
    elif method=="ping":
        destination=getDestination()
        pings=raw_input("How many times should we ping it?")
        os.system("python Traceroute.py ", destination, " ", pings)
        notDone=false
    else:
        print "We do not recognize that"

    
