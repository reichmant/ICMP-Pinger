from socket import *
import os
import sys
import struct
import time
import select
import binascii
import socket
#import antigravity																	# https://xkcd.com/353/
ICMP_ECHO_REQUEST = 8

#global shortestTime, longestTime, cumulativeTime, numberOfPackets
shortestTime = 99999999999
longestTime = -99999999999
cumulativeTime = 0
numberOfPackets = 0



def checksum(str):
	# Calculate the checksum.
	csum = 0																		# Initialize to 0
	countTo = (len(str) / 2) * 2													# Calculate upper bound
	count = 0																		# Initialize counter at 0

	while count < countTo:															# While within the bounds of the counter...
		thisVal = ord(str[count+1]) * 256 + ord(str[count])							#	Calculate the checksum
		csum = csum + thisVal
		csum = csum & 0xffffffffL
		count = count + 2

	if countTo < len(str):															# Also do some fancy checksum stuff if the upper
		csum = csum + ord(str[len(str) - 1])										# bounds of the counter are less than the length
		csum = csum & 0xffffffffL													# of the string passed in.

	csum = (csum >> 16) + (csum & 0xffff)
	csum = csum + (csum >> 16)
	answer = ~csum
	answer = answer & 0xffff
	answer = answer >> 8 | (answer << 8 & 0xff00)
	return answer


def analyzeType(ICMPtype,ICMPcode,recPacket,destAddr):
	# Takes a type and code in for the received packet/destination address
	# Prints out what type of response we got, based on type/code
	# It looks complicated, but it's just a series of IF statements, based on:
	# https://rlworkman.net/howtos/iptables/chunkyhtml/x281.html
	print "ICMP type and code are:", ICMPtype, ", ",ICMPcode
	timeReceived = time.time()
	
	if ICMPtype == 0:
			
		dataSize=struct.calcsize("d")
		
		timeSent=struct.unpack("d",recPacket[28:28 + dataSize])[0]		# get the bit containing the time sent
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

		return delay


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
		print "Unknown!"

def receiveOnePing(mySocket, ID, timeout, destAddr):
	# Gets the returned packet.
	# Extracts information (header, etc.).
	# Calculates delay.
	timeLeft = timeout

	while True:
		startedSelect = time.time()													# Mark the current time as when we started select
		whatReady = select.select([mySocket], [], [], timeLeft)
		howLongInSelect = (time.time() - startedSelect)
		if whatReady[0] == []: # Timeout
			return "Request timed out."

		
		recPacket, addr = mySocket.recvfrom(1024)
		

		icmpHeader = recPacket[20:28]												# Get the ICMP header, those 8 bytes
											# (I heard we can go further and get TTL, but we accomplished that differently)
		ICMPtype, ICMPcode, headerChecksum, packetID, sequence= struct.unpack("bbHHh", icmpHeader)	# To get TTL, we could use "bbHHhd".
																									# But we don't need that? I heard other groups needed that...

		if (packetID==ID):															# If the packet ID matches the one passed in...
			delay=analyzeType(ICMPtype, ICMPcode, recPacket, destAddr)				# Get the delay by analyzing the type/code
			return delay

		timeLeft = timeLeft - howLongInSelect
		if timeLeft <= 0:
			return "Request timed out."

			
def sendOnePing(mySocket, destAddr, ID):
	# Header is type (8), code (8), checksum (16), id (16), sequence (16)

	myChecksum = 0
	# Make a dummy header with a 0 checksum.
	# struct -- Interpret strings as packed binary data
	header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1)			# Pack the header
	data = struct.pack("d", time.time())											# Pack the data
	# Calculate the checksum on the data and the dummy header.
	myChecksum = checksum(header + data)
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
	mySocket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp) # Create a socket as defined here: https://docs.python.org/2/library/socket.html#socket.socket
	mySocket.bind(("",0))											# Binds it to the address we give it. Needs to be a tuple.

	myID = os.getpid() & 0xFFFF 									# Return the current process id
	sendOnePing(mySocket, destAddr, myID)							# Send a ping, based on above stuff (passed in)
	delay = receiveOnePing(mySocket, myID, timeout, destAddr)		# Calculate the current delay

	mySocket.close()												# Close the socket, we're done with everything we need to do with it (for now)
	return delay													# Return the delay
def ping(host, timeout=1):
	# timeout=1 means: If one second goes by without a reply from the server,
	#the client assumes that either the client's ping or the server's pong is lost

	try:
		numberOfPings = int(sys.argv[2])							# If we can, use the user's input as the number of pings to send

	except:
		numberOfPings = 10
		print "You didn't enter a valid number of pings, defaulting to 10."
	
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


	# Print all the results, including a fancy little header
	print "---------------ping statistics---------------"				
	print "number of packets received is " , numberOfPackets
	packetLossPercentage = (1 - numberOfPackets/numberOfPings)*100
	print "percentage packet loss = ", packetLossPercentage, "%"
	if numberOfPackets > 0 :
		print "round-trip min/avg/max = ", shortestTime, "/", cumulativeTime/numberOfPackets, "/", longestTime, "ms"
	return delay

ping(sys.argv[1])