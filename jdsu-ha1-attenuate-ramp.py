#!/usr/bin/python

################################################################################
# jdsu-ha1-attenuate-ramp.py
#   T Czerwonka tim.czerwonka@wisc.edu
#   https://git.doit.wisc.edu/TIMC/misc-utils/tree/master/JDSU-HA1-GPIB
#   Wed Oct 16 16:31:13 CDT 2019
#   Code to manipulate a JDSU HA1 optical attenuator via GPIB
#   Feature is a ramp up / down 
#
#   modified from
#   http://prologix.biz/downloads/arb.py
#
#   Usage: <COM port> <GPIB address> <start> <stop> <step> <delay in s>
#    e.g. ./jdsu-ha1-attenuate.py /dev/ttyUSB1 1 0 20 1 10
#          -- increase attenuation from 0 to 20dB in 1dB increments every ten seconds
#    e.g. ./jdsu-ha1-attenuate.py /dev/ttyUSB1 1 30 25 0.5 0.1
#          -- decrease attenuation from 30 to 25dB in 0.5dB increments every 0.1 second 
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
from datetime import datetime


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

	if len( sys.argv ) != 7:
		print "Usage: ", os.path.basename( sys.argv[0] ), "<COM port> <GPIB address> <start> <stop> <step> <delay>"
		sys.exit(1)

	# Prologix GPIB-USB Controller serial port
	comport = sys.argv[1];

	# JDSU GPIB address
	addr = sys.argv[2]
	
	#start value
	start = float(sys.argv[3])

	#stop value
	stop = float(sys.argv[4])

	#step value
	step = float(sys.argv[5])

	#delay value
	delay = float(sys.argv[6])

	#check validity of start and stop values - 0-40db required
	# 0-40db required
	if start < 0:
		print "start attenuation value lt zero."
		exit(1)
	if start > 40:
		print "start attenuation value gt 40 ."
		exit(1)
	if stop < 0:
		print "stop attenuation value lt zero."
		exit(1)
	if stop > 40:
		print "stop attenuation value gt 40 ."
		exit(1)

	#up or down
	if start > stop:
		step = (step * -1)

	current_attenuation = start

	try:
		# Open serial port
		ser = serial.Serial( comport, 115200, timeout=0.5 )

		# Set address
		ser.write("++addr " + addr + "\n")

		# Turn off read-after-write to avoid "Query Unterminated" errors
		ser.write("++auto 1\n")

		# Do not append CR or LF to GPIB data
		ser.write("++eos 3\n")

		# Assert EOI with last byte to indicate end of data
		ser.write("++eoi 1\n")
		time.sleep(0.5)

		#set start value
		cmd = ":INP:ATT " + str(current_attenuation)
		ser.write(cmd + "\n")
		curr_time = datetime.now()
		formatted_time = curr_time.strftime('%H:%M:%S.%f')
		print formatted_time, current_attenuation
		#delay
		time.sleep(delay)

		while 1:
			current_attenuation = current_attenuation + step
			if step < 0:
				if current_attenuation < stop:
					sys.exit(0)
			if step > 0:
				if current_attenuation > stop:
					sys.exit(0)
			cmd = ":INP:ATT " + str(current_attenuation)
			curr_time = datetime.now()
			formatted_time = curr_time.strftime('%H:%M:%S.%f')
			ser.write(cmd + "\n")
			print formatted_time, current_attenuation
			time.sleep(delay)





	except serial.SerialException, e:
		print e


