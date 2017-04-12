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
# We just copied this from the other file, since we already did it...
    csum = 0                                                            # Initialize to 0
    countTo = (len(str) / 2) * 2                                        # Calculate upper bound
    count = 0                                                           # Initialize counter at 0

    while count < countTo:                                              # While within the bounds of the counter...
        thisVal = ord(str[count+1]) * 256 + ord(str[count])             #   Calculate the checksum
        csum = csum + thisVal
        csum = csum & 0xffffffffL
        count = count + 2

    if countTo < len(str):                                              # Also do some fancy checksum stuff if the upper
        csum = csum + ord(str[len(str) - 1])                            # bounds of the counter are less than the length
        csum = csum & 0xffffffffL                                       # of the string passed in.

    csum = (csum >> 16) + (csum & 0xffff)
    csum = csum + (csum >> 16)
    answer = ~csum
    answer = answer & 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer                                                       


def build_packet():
    # Build the packet to specifications


    #Creates new checksum for packet
    theChecksum = 0                                                     # Initialize at 0
    ID = os.getpid() & 0xFFFF                                           # Gets ID of packet

    
    
    ICMPHeader = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, theChecksum, ID, 1)     # Creates header with checksum of 0
    

    payload = struct.pack("d", time.time())                             # Make the body of the ICMP the current time

    
    theChecksum = checksum(ICMPHeader + payload)                        # Creates proper checksum for packet (calculated from header and payload combined)

    theChecksum = htons(theChecksum)                                    # We need to convert the checksum from host to network byte order
                                                                        # Source: https://docs.python.org/2/library/socket.html#socket.htons

    
    ICMPHeader = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, theChecksum, ID, 1)     #Fully constructs the new header with the new checksum

    packet = ICMPHeader + payload                                       # Combine header with body

    return packet                                                       # Return the fully built packet


def get_route(hostname):
    timeLeft = TIMEOUT
    for ttl in xrange(1,MAX_HOPS):
        for tries in xrange(TRIES):
            destAddr = gethostbyname(hostname)
            

            
            protocol = socket.getprotobyname("icmp")                    # Get the protocol for icmp. Thank God for this function!

            mySocket = socket.socket(socket.AF_INET, socket.SOCK_RAW, protocol)     # Make a raw socket named mySocket

            # The rest of the stuff was given... comments may not be accurate here!
            mySocket.setsockopt(IPPROTO_IP, IP_TTL, struct.pack('I', ttl))          # Do stuff with mySocket
            mySocket.settimeout(TIMEOUT)

            try:                                                        # Attempt to...
                d = build_packet()                                                  # Get the built packet
                mySocket.sendto(d, (hostname, 0))                                   # Send it to mySocket
                t = time.time()                                                     # Get the current time (why do we need t?)
                startedSelect = time.time()                                         # Same here
                whatReady = select.select([mySocket], [], [], timeLeft)             # Select the stuff in the socket(?)
                howLongInSelect = (time.time() - startedSelect)                     # Count down the remaining time
                if whatReady[0] == []: # Timeout                                    # Timeout if nothing was selected (AKA received?)
                    print " * * * Request timed out."
                recvPacket, addr = mySocket.recvfrom(1024)                          # Populate the received packet and address
                timeReceived = time.time()                                          # Set time received to the current time
                timeLeft = timeLeft - howLongInSelect                               # (Re)calculate time left
                if timeLeft <= 0:                                                   # Timeout when no time's left
                    print " * * * Request timed out."
            except timeout:
                continue                                                            # Try again as soon as we timeout, from beginning
            else:                                                       # When there's no timeout...

                # Fetch the icmp type from the IP packet
                icmpHeader = recvPacket[20:28]
                
                ICMPType, ICMPcode, headerChecksum, packetID, sequence= struct.unpack("bbHHh", icmpHeader) # we don't need anything besides ICMPType ("b")

                #ICMPType = struct.unpack("d", icmpHeader)                                  # why doesn't this work!?

                # Do different things depending on the ICMP type
                # Types are dictated here to keep comments clean:
                # https://rlworkman.net/howtos/iptables/chunkyhtml/x281.html
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
get_route(sys.argv[1])                                                  # Basically, this file just calls get_route
                                                                        # The user is supposed to give us a url/IP