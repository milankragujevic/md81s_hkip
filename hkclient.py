#!/usr/bin/env python
import os
import socket
import sys, traceback
import time
import random
import struct
import numpy as np
import cv2

UDP_IP_HOST = "192.168.1.28"
UDP_PORT_HOST = 5123
UDP_IP_TARGET = "192.168.1.1"
UDP_PORT_TARGET = 5000
SOCKET_TIMEOUT = 2
SAVE_PATH = "/root/hkclient/strange"
NB_FRAGMENTS_TO_ACCUMULATE = 80

MESSAGE_43 = bytearray([ 0x00, 0x00, 0xb0, 0x02, 0x82, 0x00, 0x00, 0x27, 0x00, 0x01, 0x00, 0x00, 0x00, 0x4d, 0x61, 0x63, 0x49, 0x50, 0x3d, 0x42, 0x43, 0x2d, 0x41, 0x45, 0x2d, 0x43, 0x35, 0x2d, 0x37, 0x43, 0x2d, 0x37, 0x37, 0x2d, 0x37, 0x42, 0x2b, 0x31, 0x36, 0x34, 0x36, 0x37, 0x3b ])
MESSAGE_13_1 = bytearray([ 0x00, 0x00, 0xd0, 0x00, 0x82, 0x00, 0x06, 0x09, 0x00, 0x01, 0x00, 0x00, 0x00 ])
MESSAGE_13_2 = bytearray([ 0x00, 0x00, 0xd0, 0x00, 0xa2, 0x00, 0x06, 0x09, 0x00, 0x01, 0x00, 0x00, 0x00 ])
MESSAGE_13_3 = bytearray([ 0x00, 0x00, 0xd0, 0x00, 0x62, 0x00, 0x06, 0x09, 0x00, 0x01, 0x00, 0x00, 0x00 ])
MESSAGE_212 = bytearray([ 0x01, 0x00, 0x40, 0x0d, 0x32, 0x00, 0x00, 0xd0, 0x00, 0x51, 0x01, 0x00, 0x00, 0x69, 0x64, 0xd4, 0xd8, 0xd8, 0xd2, 0x8f, 0x9d, 0xa7, 0xd9, 0xd4, 0x9f, 0x80, 0x8d, 0x8c, 0x86, 0xc7, 0x9f, 0x8b, 0xbf, 0x80, 0x8d, 0x8c, 0x86, 0xc7, 0xa4, 0xb9, 0xac, 0xae, 0xdd, 0xd2, 0x8f, 0x9d, 0xa7, 0xd8, 0xd4, 0x87, 0x8c, 0x9d, 0xc7, 0xd9, 0xd2, 0x8f, 0x9d, 0xa7, 0xdb, 0xd4, 0xa1, 0xa2, 0xb9, 0xaa, 0xb9, 0x9b, 0x8c, 0x9a, 0x8c, 0x87, 0x9d, 0xc7, 0xa1, 0xa2, 0xb9, 0xaa, 0xb9, 0x9b, 0x8c, 0x9a, 0x8c, 0x87, 0x9d, 0xd2, 0x86, 0x99, 0xa7, 0xdb, 0xd4, 0xdc, 0x98, 0x8d, 0xdf, 0xa6, 0xa3, 0xdf, 0xda, 0xda, 0xdf, 0xde, 0x8f, 0x8f, 0x8f, 0xd2, 0xaa, 0x88, 0x85, 0x85, 0x80, 0x8d, 0xd4, 0xdd, 0x85, 0x90, 0xd9, 0x81, 0x8f, 0xdc, 0x82, 0xd8, 0xde, 0xa8, 0xd9, 0xd9, 0xae, 0xb3, 0xd8, 0xd0, 0x8f, 0xda, 0x85, 0xdc, 0xde, 0xad, 0x8a, 0xdf, 0xda, 0xda, 0xdf, 0xd9, 0x8f, 0x8f, 0xd9, 0xd2, 0x9a, 0x80, 0x8d, 0xa7, 0xd4, 0xdc, 0x98, 0x8d, 0xdf, 0xa6, 0xa3, 0xdf, 0xda, 0xda, 0xdf, 0xde,  0x8f, 0x8f, 0x8f, 0xd2, 0xa8, 0x9a, 0xaa, 0x86, 0x8d, 0x8c, 0xd4, 0xda, 0xda, 0xde, 0xd2, 0xa4, 0x88, 0x80, 0x87, 0xaa, 0x84, 0x8d, 0xd4, 0xa1, 0xa2, 0xb6, 0xbb, 0xac, 0xba, 0xb6, 0xbb, 0xac, 0xb8, 0xd2, 0x9c, 0x9a, 0x8c, 0x9b, 0xd4, 0xd8, 0xd0, 0xdb, 0xc7, 0xd8, 0xdf, 0xd1, 0xc7, 0xd9, 0xc7, 0xda, 0xda, 0xd2 ])
MESSAGE_34 = bytearray([ 0x00, 0x00, 0x20, 0x02, 0x12, 0x00, 0x00, 0x1e, 0x00, 0x01, 0x00, 0x00, 0x00, 0xa0, 0xaa, 0xa4, 0xad, 0xd4, 0xd8, 0xd2, 0xba, 0xac, 0xb8, 0xd4, 0xd8, 0xd2, 0xbd, 0xa0, 0xa4, 0xac, 0xd4, 0xd9, 0xd2, 0xe9 ])
MESSAGE_119 = bytearray([ 0x02, 0x00, 0x70, 0x07, 0x32, 0x00, 0x00, 0x73, 0x00, 0x64, 0x00, 0x00, 0x00, 0x4d, 0x61, 0x80, 0x87, 0xaa, 0x84, 0x8d, 0xd4, 0xba, 0x8c, 0x9a, 0x9a, 0x80, 0x86, 0x87, 0xba, 0x9d, 0x88, 0x9b, 0x9d, 0xd2, 0x9a, 0x80, 0x8d, 0xa7, 0xd4, 0xdc, 0x98, 0x8d, 0xdf, 0xa6, 0xa3, 0xdf, 0xda, 0xda, 0xdf, 0xde, 0x8f, 0x8f, 0x8f, 0xd2, 0x8f, 0x9d, 0xa7, 0xd9, 0xd4, 0xa1, 0xa2, 0xb9, 0xaa, 0xb9, 0x9b, 0x8c, 0x9a, 0x8c, 0x87, 0x9d, 0xc7, 0xa1, 0xa2, 0xb9, 0xaa, 0xb9, 0x9b, 0x8c, 0x9a, 0x8c, 0x87, 0x9d, 0xd2, 0xaf, 0xad, 0xd9, 0xd4, 0xdb, 0xdc, 0xd8, 0xdd, 0xd0, 0xdb, 0xd1, 0xd1, 0xd2, 0x8f, 0x9d, 0xa7, 0xd8, 0xd4, 0x87, 0x8c, 0x9d, 0xc7, 0xd8, 0xd9, 0xdb, 0xdc, 0xd2, 0xaf, 0xad, 0xd8, 0xd4, 0xd8, 0xd9, 0xdb, 0xdc, 0xd2 ])
MESSAGE_CONTINUE_BEGIN = bytearray([ 0x00, 0x00, 0xff, 0x02, 0x12, 0x00, 0x00, 0xff, 0x00, 0x01, 0x00, 0x00, 0x00, 0xa0, 0xaa, 0xa4, 0xad, 0xd4, 0xd8, 0xd2, 0xba, 0xac, 0xb8, 0xd4 ])
MESSAGE_CONTINUE_END = bytearray([ 0xd2, 0xbd, 0xa0, 0xa4, 0xac, 0xd4, 0xd9, 0xd2, 0xe9 ])
CONTINUE_LIST_2 = bytearray([ 0xd9, 0xd8, 0xdb, 0xda, 0xdd, 0xdc, 0xdf, 0xde, 0xd1, 0xd0 ])
CONTINUE_LIST_1 = bytearray([ 0xd8, 0xdf, 0xdb, 0xde, 0xda, 0xd1, 0xdd, 0xd0, 0xdc, 0xd9, 0xdf, 0xd8, 0xde, 0xdb, 0xd1, 0xda, 0xd0, 0xdd, 0xd9, 0xdc ])

buffer = bytearray(1024)

msg = bytearray()

sock = False

def byteToInt(byteVal):
	return struct.unpack('B', byteVal[0])[0]

def sendControlPacket(packet):
	sock.sendto(packet, (UDP_IP_TARGET, UDP_PORT_TARGET))	

def sendContinuePacket(packet):
	sock.sendto(packet, (UDP_IP_TARGET, UDP_PORT_TARGET))
	
def receiveControlPacket(output):
	sock.settimeout(SOCKET_TIMEOUT)
	nbbytes, addr = sock.recvfrom_into(output, 1024)
	return nbbytes
	
def dumpDebugImage(image):
	seqc = str(int(time.time())) 
	cv2.imwrite(SAVE_PATH + "/" + seqc + ".jpg", image)

while True:
	val = random.randint(0,16)
	MESSAGE_13_1[6] = val
	MESSAGE_13_2[6] = val
	MESSAGE_13_3[6] = val
	msg = b''
	inImage = False
	imageIndex = 0
	lastFragmentId = 0
	fragmentIndex = 0
	nbDigits = 1
	continue_index = [0,0,0,0,0]
	base_index = 0
	fragments_received = 0
	bytes=''
	latestBeepTime = 0 
	socket_error = False
	nbDifferences = 0
	imagesToCapture = 0
	
	if sock: 
		sock.close()
		
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock.bind((UDP_IP_HOST, UDP_PORT_HOST))
	
	sendControlPacket(MESSAGE_43)
	sendControlPacket(MESSAGE_13_1)
	
	for i in range(5):
			nbReceived = receiveControlPacket(buffer)
			if ((nbReceived == 13) and (buffer[4] == (MESSAGE_13_1[4] | 0b00010000)) and (buffer[6] != (MESSAGE_13_1[6] | 0b01000000))):
				break
			else:
				if (i==9):
					exit()
	
	sendControlPacket(MESSAGE_13_2)
	sendControlPacket(MESSAGE_13_3)
	
	nbReceived = receiveControlPacket(buffer)
	if (nbReceived != 13):
		exit()
	
	sendControlPacket(MESSAGE_212)
	
	nbReceived = receiveControlPacket(buffer)
	if(nbReceived == 42):
		nbReceived = receiveControlPacket(buffer)
	if (nbReceived != 155 and nbReceived != 156):
		exit()
	
	sendControlPacket(MESSAGE_34)
	sendControlPacket(MESSAGE_119)
	
	nbReceived = receiveControlPacket(buffer)
	if(nbReceived == 42):
		nbReceived = receiveControlPacket(buffer)
	if (nbReceived != 362 and nbReceived != 368):
		exit()
	
	while socket_error == False:
		sock.settimeout(SOCKET_TIMEOUT)
		try:
			chunk = sock.recv(1024)
		except: 
			socket_error = True
			continue
		nbbytes = len(chunk)
		fragments_received += 1
		fragmentIndex += 1
		if (fragments_received <= NB_FRAGMENTS_TO_ACCUMULATE):
			if nbbytes >= 17:
				if (chunk[15] == '\xff') and (chunk[16] == '\xd8'):
					lastFragmentId = byteToInt(chunk[0])
					msg+= chunk[15:]
				else:
					if ((byteToInt(chunk[0]) == lastFragmentId+1) or (byteToInt(chunk[0]) == 0) and (lastFragmentId==255)):
						msg += chunk[4:]
					else:
						msg = b''
						fragments_received = 0
					lastFragmentId = byteToInt(chunk[0])
			else:
				msg = b''
				fragments_received = 0
		else:
			SOI_index = -1
			EOI_index = -1
			for index in range(0,len(msg)-1):
				if (msg[index] == '\xff'):
					if msg[index+1] == '\xd8':
						SOI_index = index
						for index in range(index+2,len(msg)-1):
							if (msg[index] == '\xff'):
								if msg[index+1] == '\xd9':
									EOI_index = index
									break
						break
			if SOI_index!=-1 and EOI_index!=-1:
				jpeg = msg[SOI_index:EOI_index+2]
				msg = msg[EOI_index+2:]
				RGBImage = cv2.imdecode(np.fromstring(jpeg, dtype=np.uint8), 1)
				dumpDebugImage(RGBImage)
				imageIndex += 1
			msg = b''
			fragments_received = 0
		if (fragmentIndex%5) == 0:
			tmp = bytearray()
			if (nbDigits == 1):
				MESSAGE_CONTINUE_BEGIN[2] = 0x20
				MESSAGE_CONTINUE_BEGIN[7] = 0x1e
				tmp.append(CONTINUE_LIST_1[base_index+continue_index[0]])
				continue_index[0] += 1
				if continue_index[0] == 2:
					nbDigits += 1
					continue_index[1] = 1 
					continue_index[0] = 0
			elif (nbDigits == 2):
				MESSAGE_CONTINUE_BEGIN[2] = 0x30
				MESSAGE_CONTINUE_BEGIN[7] = 0x1f
				tmp.append(CONTINUE_LIST_2[continue_index[1]])
				tmp.append(CONTINUE_LIST_1[base_index+continue_index[0]])
				continue_index[0] += 1
				if continue_index[0] == 2:
					continue_index[1] += 1
					continue_index[0] = 0
				if continue_index[1] == len(CONTINUE_LIST_2):
					nbDigits += 1
					continue_index[2] = 1 
					continue_index[1] = 0 
					continue_index[0] = 0
			elif (nbDigits == 3):
				MESSAGE_CONTINUE_BEGIN[2] = 0x40
				MESSAGE_CONTINUE_BEGIN[7] = 0x20
				tmp.append(CONTINUE_LIST_2[continue_index[2]])
				tmp.append(CONTINUE_LIST_2[continue_index[1]])
				tmp.append(CONTINUE_LIST_1[base_index+continue_index[0]])
				continue_index[0] += 1
				if continue_index[0] == 2:
					continue_index[1] += 1
					continue_index[0] = 0
				if continue_index[1] == len(CONTINUE_LIST_2):
					continue_index[2] += 1
					continue_index[1] = 0 
					continue_index[0] = 0
				if continue_index[2] == len(CONTINUE_LIST_2):
					nbDigits += 1
					continue_index[3] = 1 
					continue_index[2] = 0 
					continue_index[1] = 0 
					continue_index[0] = 0 
			elif (nbDigits == 4):
				MESSAGE_CONTINUE_BEGIN[2] = 0x50
				MESSAGE_CONTINUE_BEGIN[7] = 0x21
				tmp.append(CONTINUE_LIST_2[continue_index[3]])
				tmp.append(CONTINUE_LIST_2[continue_index[2]])
				tmp.append(CONTINUE_LIST_2[continue_index[1]])
				tmp.append(CONTINUE_LIST_1[base_index+continue_index[0]])
				continue_index[0] += 1
				if continue_index[0] == 2:
					continue_index[1] += 1
					continue_index[0] = 0
				if continue_index[1] == len(CONTINUE_LIST_2):
					continue_index[2] += 1
					continue_index[1] = 0 
					continue_index[0] = 0
				if continue_index[2] == len(CONTINUE_LIST_2):
					continue_index[3] += 1 
					continue_index[2] = 0 
					continue_index[1] = 0 
					continue_index[0] = 0 
				if continue_index[3] == len(CONTINUE_LIST_2):
					nbDigits += 1
					continue_index[4] = 1 
					continue_index[3] = 0 
					continue_index[2] = 0 
					continue_index[1] = 0 
			elif (nbDigits == 5):
				MESSAGE_CONTINUE_BEGIN[2] = 0x60
				MESSAGE_CONTINUE_BEGIN[7] = 0x22
				tmp.append(CONTINUE_LIST_2[continue_index[4]])
				tmp.append(CONTINUE_LIST_2[continue_index[3]])
				tmp.append(CONTINUE_LIST_2[continue_index[2]])
				tmp.append(CONTINUE_LIST_2[continue_index[1]])
				tmp.append(CONTINUE_LIST_1[base_index+continue_index[0]])
				continue_index[0] += 1
				if continue_index[0] == 2:
					continue_index[1] += 1
					continue_index[0] = 0
				if continue_index[1] == len(CONTINUE_LIST_2):
					continue_index[2] += 1
					continue_index[1] = 0 
					continue_index[0] = 0
				if continue_index[2] == len(CONTINUE_LIST_2):
					continue_index[3] += 1 
					continue_index[2] = 0 
					continue_index[1] = 0 
					continue_index[0] = 0 
				if continue_index[3] == len(CONTINUE_LIST_2):
					continue_index[4] += 1 
					continue_index[3] = 0 
					continue_index[2] = 0 
					continue_index[1] = 0 
					continue_index[0] = 0 
				if continue_index[4] == len(CONTINUE_LIST_2):
					nbDigits = 1
			if len(tmp) == 5 and tmp.startswith(b'\xdf\xdc\xdd\xd0'):
				nbDigits = 1
			if (fragmentIndex % 100 == 0):
				base_index = (base_index + 2) % 20  
			packet = MESSAGE_CONTINUE_BEGIN + tmp + MESSAGE_CONTINUE_END
			sendContinuePacket(packet)
