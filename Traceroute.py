from socket import *
import os
import sys
import struct
import time
import select
import binascii
import socket

ICMP_ECHO_REQUEST = 8
MAX_HOPS = 30
TIMEOUT = 2.0
TRIES = 2
# The packet that we shall send to each router along the path is the ICMP echo
# request packet, which is exactly what we had used in the ICMP ping exercise.
# We shall use the same packet that we built in the Ping exercise
def checksum(str):
# In this function we make the checksum of our packet
# hint: see icmpPing lab

    csum = 0
    countTo = (len(str) / 2) * 2
    count = 0

    while count < countTo:
        thisVal = ord(str[count+1]) * 256 + ord(str[count])
        csum = csum + thisVal
        csum = csum & 0xffffffffL
        count = count + 2

    if countTo < len(str):
        csum = csum + ord(str[len(str) - 1])
        csum = csum & 0xffffffffL

    csum = (csum >> 16) + (csum & 0xffff)
    csum = csum + (csum >> 16)
    answer = ~csum
    answer = answer & 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer



def build_packet():

    #Creates new checksum for packet
    theChecksum = 0
    #Gets ID of packet
    ID = os.getpid() & 0xFFFF

    
    #creates header with checksum of 0
    ICMPHeader = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, theChecksum, ID, 1)
    

    #make the body of the ICMP the current time
    payload = struct.pack("d", time.time())

    # Creates proper checksum for packet
    theChecksum = checksum(ICMPHeader + payload)    

    theChecksum = htons(theChecksum)

    #Fully constructs the new header with the new checksum
    ICMPHeader = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, theChecksum, ID, 1)

    #Combine header with body
    packet = ICMPHeader + payload

    return packet
#####################################################


def get_route(hostname):
    timeLeft = TIMEOUT
    for ttl in xrange(1,MAX_HOPS):
        for tries in xrange(TRIES):
            destAddr = gethostbyname(hostname)
            
            #Fill in start

            # Make a raw socket named mySocket
            protocol = socket.getprotobyname("icmp")     # the same as when we did this in the other file

            mySocket = socket.socket(socket.AF_INET, socket.SOCK_RAW, protocol)

            #Fill in end

            mySocket.setsockopt(IPPROTO_IP, IP_TTL, struct.pack('I',    ttl))
            mySocket.settimeout(TIMEOUT)

            try:
                d = build_packet()
                mySocket.sendto(d, (hostname, 0))
                t = time.time()
                startedSelect = time.time()
                whatReady = select.select([mySocket], [], [], timeLeft)
                howLongInSelect = (time.time() - startedSelect)
                if whatReady[0] == []: # Timeout
                    print " * * * Request timed out."
                recvPacket, addr = mySocket.recvfrom(1024)
                timeReceived = time.time()
                timeLeft = timeLeft - howLongInSelect
                if timeLeft <= 0:
                    print " * * * Request timed out."
            except timeout:
                continue
            else:

                # Fetch the icmp type from the IP packet
                icmpHeader = recvPacket[20:28]
                
                ICMPType, ICMPcode, headerChecksum, packetID, sequence= struct.unpack("bbHHh", icmpHeader) # we don't need anything besides ICMPType ("b")

                #ICMPType = struct.unpack("d", icmpHeader)                                  # why doesn't this work!?

                if ICMPType == 11:
                    bytes = struct.calcsize("d")
                    timeSent = struct.unpack("d", recvPacket[28:28 + bytes])[0]
                    print " %d rtt=%.0f ms %s" %(ttl, (timeReceived -t)*1000, addr[0])
                elif ICMPType == 3:
                    bytes = struct.calcsize("d") 
                    timeSent = struct.unpack("d", recvPacket[28:28 + bytes])[0]
                    print " %d rtt=%.0f ms %s" %(ttl, (timeReceived-t)*1000, addr[0])
                elif ICMPType == 0:
                    bytes = struct.calcsize("d")
                    timeSent = struct.unpack("d", recvPacket[28:28 + bytes])[0]
                    print " %d rtt=%.0f ms %s" %(ttl, (timeReceived - timeSent)*1000, addr[0])
                    return
                else:
                    print "Error - no ICMP types"
                break
            finally:
                mySocket.close()
get_route("google.com")
