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
# In the sendOnePing() method of the ICMP Ping exercise ,firstly the header of our
# packet to be sent was made, secondly the checksum was appended to the header and
# then finally the complete packet was sent to the destination.
# Make the header in a similar way to the ping exercise.
# Append checksum to the header.
# Don’t send the packet yet , just return the final packet in this function.
# So the function ending should look like this
# Make the header in a similar way to the ping exercise.
####################################################

    #Rewrite comments


    # Header is type (8), code (8), checksum (16), id (16), sequence (16)
    theChecksum = 0
    ID = os.getpid() & 0xFFFF

    # Make a dummy header with a 0 checksum.
    # struct -- Interpret strings as packed binary data
    ICMPHeader = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, theChecksum, ID, 1)
    
    payload = struct.pack("d", time.time())

    # Calculate the checksum on the data and the dummy header.
    # Append checksum to the header.
    theChecksum = checksum(ICMPHeader + payload)    
    if sys.platform == 'darwin':
        theChecksum = socket.htons(theChecksum) & 0xffff
        #Convert 16-bit integers from host to network byte order.
    else:
        theChecksum = htons(theChecksum)

    ICMPHeader = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, theChecksum, ID, 1)
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
            protocol = socket.getprotobyname("icmp")
            mySocket = socket.socket(socket.AF_INET, socket.SOCK_RAW, protocol)
            #Fill in end

            mySocket.setsockopt(IPPROTO_IP, IP_TTL, struct.pack('I',    ttl))
            mySocket.settimeout(TIMEOUT)

            try:
                d = build_packet()
                mySocket.sendto(d, (hostname, 0))
                t= time.time()
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
                #Fill in start
                # Fetch the icmp type from the IP packet
                icmpHeader = recvPacket[20:28]
                ICMPType, ICMPcode, HeaderChecksum, packetID, sequence = struct.unpack("bbHHh", icmpHeader)
                #Fill in end
                if type == 11:
                    bytes = struct.calcsize("d")
                    timeSent = struct.unpack("d", recvPacket[28:28 + bytes])[0]
                    print " %d rtt=%.0f ms %s" %(ttl, (timeReceived -t)*1000, addr[0])
                elif type == 3:
                    bytes = struct.calcsize("d") 
                    timeSent = struct.unpack("d", recvPacket[28:28 + bytes])[0]
                    print " %d rtt=%.0f ms %s" %(ttl, (timeReceived-t)*1000, addr[0])
                elif type == 0:
                    bytes = struct.calcsize("d")
                    timeSent = struct.unpack("d", recvPacket[28:28 + bytes])[0]
                    print " %d rtt=%.0f ms %s" %(ttl, (timeReceived - timeSent)*1000, addr[0])
                    return
                else:
                    print "error"
                break
            finally:
                mySocket.close()
get_route("google.com")
