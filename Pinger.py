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
    return raw_input("What address should we ping? \n")

notDone=True
while notDone:
    method=raw_input("To ping a server type 'ping' or to traceroute a server type 'trace' \n")
    if method=="trace":
        destination=getDestination()
        command= "sudo python Traceroute.py "+ destination
        os.system(command)
        notDone=False
    elif method=="ping":
        destination=getDestination()
        pings=raw_input("How many times should we ping it? \n")
        command="sudo python 'ICMP Pinger.py' "+ destination+ " "+ pings
        os.system(command)
        notDone=False
    else:
        print "We do not recognize that. \n"

os.system("sl")  
os.system("cowsay I Like Eggs")