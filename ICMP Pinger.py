from socket import *
import os
import sys
import struct
import time
import select
import binascii
import socket
ICMP_ECHO_REQUEST = 8

#global shortestTime, longestTime, cumulativeTime, numberOfPackets
shortestTime = 99999999999
longestTime = -99999999999
cumulativeTime = 0
numberOfPackets = 0



def checksum(str):
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
def receiveOnePing(mySocket, ID, timeout, destAddr):
	timeLeft = timeout
 
	while True:
		startedSelect = time.time()																				
		whatReady = select.select([mySocket], [], [], timeLeft)
		howLongInSelect = (time.time() - startedSelect)
		if whatReady[0] == []: # Timeout
			return "Request timed out."

		timeReceived = time.time()
		recPacket, addr = mySocket.recvfrom(1024)
		
################################

		icmpHeader = recPacket[20:28]																							# get the ICMP header
		ICMPtype, ICMPcode, headerChecksum, packetID, sequence = struct.unpack("bbHHh", icmpHeader) # change later
		print "ICMP type is:", ICMPtype

		if ICMPtype == 0:
			
			if (packetID==ID):
				dataSize=struct.calcsize("d")
				
				timeSent=struct.unpack("d",recPacket[28:28 + dataSize])[0]					# get the bit containing the time sent
				delay = timeReceived - timeSent
				global shortestTime
				global longestTime
				global cumulativeTime
				global numberOfPackets
				if delay < shortestTime:
					shortestTime = delay
				if delay > longestTime:
					longestTime = delay
				cumulativeTime += delay
				numberOfPackets += 1
	
	
				print ("Reply from " + str(destAddr) + ":" + " bytes=" + str(dataSize) + " " )

		elif ICMPtype == 1:
			print "ERROR: Unreachable!"
			if ICMPcode == 0:
				print "Code 0 - Network unreachable"
			elif ICMPcode == 1:
				print "Code 1 - Host unreachable"
			elif ICMPcode == 2:
				print "Code 2 - Protocol unreachable"
			elif ICMPcode == 3:
				print "Code 3 - Port unreachable"
			elif ICMPcode == 4:
				print "Code 4 - Fragmentation needed and DF set"
			elif ICMPcode == 5:
				print	"Code 5 - Source route failed"
			elif ICMPcode == 6:
				print	"Code 6 - Destination network unknown"
			elif ICMPcode == 7:
				print	"Code 7 - Destination host unknown"
			else:
				print "Unknown Code"

		elif ICMPtype == 4:
			print "Source Quench!"

		elif ICMPtype == 11:
			print "ERROR: TTL is 0!"
			if ICMPcode == 0:
				print "Code 0 - TTL is 0 during transit"
			elif ICMPcode == 1:
				print "Code 1 - TTL is 0 during reassembly"

		elif ICMPtype == 12:
			print "ERROR: Parameter problem!"
			if ICMPcode == 0:
				print "Code 0 - IP header bad"
			elif ICMPcode == 1:
				print "Code 1 - Required options missing"
		else:
			print "Unspecified ICMP type!"

		
		return delay

		#global packetsreceived
		 
		#packetsreceived=packetsreceived+1
################################
		timeLeft = timeLeft - howLongInSelect
		if timeLeft <= 0:
			return "Request timed out."
def sendOnePing(mySocket, destAddr, ID):
	# Header is type (8), code (8), checksum (16), id (16), sequence (16)

	myChecksum = 0
	# Make a dummy header with a 0 checksum.
	# struct -- Interpret strings as packed binary data
	header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1)
	data = struct.pack("d", time.time())
	# Calculate the checksum on the data and the dummy header.
	myChecksum = checksum(header + data)

	# Get the right checksum, and put in the header
	if sys.platform == 'darwin':
		myChecksum = socket.htons(myChecksum) & 0xffff
		#Convert 16-bit integers from host to network byte order.
	else:
		myChecksum = socket.htons(myChecksum)

	header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1)
	packet = header + data

	mySocket.sendto(packet, (destAddr, 1)) # AF_INET address must be tuple, not str
	#Both LISTS and TUPLES consist of a number of objects
	#which can be referenced by their position number within the object
def doOnePing(destAddr, timeout):
	icmp = socket.getprotobyname("icmp")											# Get the protocol code for ICMP
	#SOCK_RAW is a powerful socket type. For more details see:
	#http://sock-raw.org/papers/sock_raw
	#Create Socket here
	mySocket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp) # create a socket as defined here: https://docs.python.org/2/library/socket.html#socket.socket
	mySocket.bind(("",0))											# binds it to the address we give it

	myID = os.getpid() & 0xFFFF #Return the current process i
	sendOnePing(mySocket, destAddr, myID)
	delay = receiveOnePing(mySocket, myID, timeout, destAddr)

	mySocket.close()
	return delay
def ping(host, timeout=1):
	#timeout=1 means: If one second goes by without a reply from the server,
	#the client assumes that either the client's ping or the server's pong is lost

	
	if sys.argv[2] > 0:
		numberOfPings = int(sys.argv[2])
	else:
		numberOfPings = 10
	dest = socket.gethostbyname(host)
	print "Pinging " + dest + " using Python:"
	print ""
	
	#Send ping requests to a server separated by approximately one second
	for i in range(numberOfPings):
		delay = doOnePing(dest, timeout)
		if type(delay) == str:
			print delay
		else:			
			print "time =",delay, "ms\n"
		time.sleep(1) # one second
	print "---------------ping statistics---------------"
	print "number of packets received is " , numberOfPackets
	packetLossPercentage = (1 - numberOfPackets/numberOfPings)*100
	print "percentage packet loss = ", packetLossPercentage, "%"
	if numberOfPackets > 0 :
		print "round-trip min/avg/max = ", shortestTime, "/", cumulativeTime/numberOfPackets, "/", longestTime, "ms"
	return delay
ping(sys.argv[1])

