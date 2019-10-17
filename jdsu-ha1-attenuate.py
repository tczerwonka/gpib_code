#!/usr/bin/python

################################################################################
# jdsu-ha1-attenuate.py
#   T Czerwonka tim.czerwonka@wisc.edu
#   https://git.doit.wisc.edu/TIMC/misc-utils/tree/master/JDSU-HA1-GPIB
#   Wed Oct 16 16:31:13 CDT 2019
#   Code to manipulate a JDSU HA1 optical attenuator via GPIB
#   modified from
#   http://prologix.biz/downloads/arb.py
#
#   Usage: <COM port> <GPIB address> <[attenuation value|block|unblock|read]>
#    e.g. ./jdsu-ha1-attenuate.py /dev/ttyUSB1 1 23.3
#
#   USB adapter here: 
#     http://egirland.blogspot.com/2014/03/arduino-uno-as-usb-to-gpib-controller.html
#
################################################################################


import os.path
import sys
import array
import time
import serial


# Special characters to be escaped
LF   = 0x0A
CR   = 0x0D
ESC  = 0x1B
PLUS = 0x2B


#==============================================================================
def IsSpecial(data):
	return data in (LF, CR, ESC, PLUS)

	
#==============================================================================
def CheckError():
	ser.write("SYST:ERR?\n")
	ser.write("++read eoi\n")
	s = ser.read(100)
	print s


#==============================================================================
def CheckResult():
	ser.write("++read eoi\n")
	s = ser.read(100)
	print s

#==============================================================================
if __name__ == '__main__':
	getresult = 0

	if len( sys.argv ) != 4:
		print "Usage: ", os.path.basename( sys.argv[0] ), "<COM port> <GPIB address> <[attenuation value|block|unblock|read|reset|idn]>"
		sys.exit(1)

	# Prologix GPIB-USB Controller serial port
	comport = sys.argv[1];

	# JDSU GPIB address
	addr = sys.argv[2]
	
	# command value
	operation = sys.argv[3]

	#argv3 is going to be either a number or a command -- figure it out
	try:
		attenuation = float(operation)
		# 0-40db required
		if attenuation < 0:
			print "attenuation value less than 0"
			exit(1)
		if attenuation > 40:
			print "attenuation value greater than 40"
			exit(1)
		cmd = ":INP:ATT " + str(attenuation)

	except:
		if operation == "idn":
			cmd = "*IDN?"
			getresult = 1
		if operation == "reset":
			cmd = "*RST"
		if operation == "block":
			cmd = ":OUTP OFF"
		if operation == "unblock":
			cmd = ":OUTP:STAT ON"
		if operation == "read":
			cmd = ":INP:ATT?"
			getresult = 1

	try:
		cmd
	except:
		print "Usage: ", os.path.basename( sys.argv[0] ), "<COM port> <GPIB address> <[attenuation value|block|unblock|read|reset|idn]>"
		sys.exit(1)


	try:
		# Open serial port
		ser = serial.Serial( comport, 115200, timeout=0.5 )

		# Set address
		ser.write("++addr " + addr + "\n")

		# Turn off read-after-write to avoid "Query Unterminated" errors
		ser.write("++auto 0\n")

		# Do not append CR or LF to GPIB data
		ser.write("++eos 3\n")

		# Assert EOI with last byte to indicate end of data
		ser.write("++eoi 1\n")
		time.sleep(1)
		ser.flushInput()

		#send the one-time command here
		ser.write(cmd + "\n")
		time.sleep(0.5)
		if getresult:
			CheckResult()

	except serial.SerialException, e:
		print e
