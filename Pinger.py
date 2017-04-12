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


notDone=True
while notDone:
    method=raw_input("To ping a server type 'ping' or to traceroute a server type 'trace' \n")
    if method=="trace":
        pass
        notDone=false
    elif method=="ping":
        pass
        notDone=false
    else:
        print "We do not recognize that"
        
    
