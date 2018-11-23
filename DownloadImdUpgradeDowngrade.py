#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import serial
import time
import os
import glob

from ctypes import *
from urllib2 import urlopen
import urllib
import re

open("output.txt", "w").close()
	
#Function to Download Image file if not found
def get_image_from_server(option):
	urlpath =urlopen('http://127.0.0.1:7000')
	string = urlpath.read().decode('utf-8')
	pattern = re.compile('([-\w]+\.(?:img))') #the pattern actually creates duplicates in the list
	imagefile = pattern.findall(string)
	imagefile = imagefile[0]
	url = "http://127.0.0.1:7000/"+imagefile
	destfilename="/tftpboot/"+option+imagefile
	urllib.urlretrieve (url,destfilename)
	with open("output.txt", "a") as f:
    		f.write("\nImage file is downloaded from"+url+" and saved in "+destfilename)
	return
	
#Function to Download Image file if not found
def get_image_from_server(option):
	urlpath =urlopen('http://127.0.0.1:7000')
	string = urlpath.read().decode('utf-8')
	pattern = re.compile('([-\w]+\.(?:img))') #the pattern actually creates duplicates in the list
	imagefile = pattern.findall(string)
	imagefile = imagefile[0]
	url = "http://127.0.0.1:7000/"+imagefile
	destfilename="/tftpboot/"+option+imagefile
	urllib.urlretrieve (url,destfilename)

#Function To Interface Name
def get_interfaces():
    libc = CDLL('libc.so.6')
    libc.getifaddrs.restype = c_int
    ifaddr_p = pointer(Ifaddrs())
    ret = libc.getifaddrs(pointer((ifaddr_p)))
    interfaces = set()
    head = ifaddr_p
    while ifaddr_p:
        interfaces.add(ifaddr_p.contents.ifa_name)
        ifaddr_p = ifaddr_p.contents.ifa_next
    libc.freeifaddrs(head) 
    ethernet_start_letter = ['e']
    iname = [name for name in interfaces if (name[0] in ethernet_start_letter)]
    iname = iname[0]
    return iname

#Function check Ethernet cable connected or not
def get_LANstatus():
    iname = get_interfaces()
    filename=os.path.join('/sys/class/net', '%s'% iname, 'operstate')
    LAN_file = open(filename,"r")
    LAN = LAN_file.readlines()
    LAN = LAN[0]
    if LAN == "up\n":
	print("LAN cable connected")
    elif LAN == "down\n":
	print("LAN cable not connected")
	with open("output.txt", "a") as f:
    		f.write("Build Failed-LAN cable not connected")
	sys.exit()
    LAN_file.close()
    return

class Sockaddr(Structure):
    _fields_ = [('sa_family', c_ushort), ('sa_data', c_char * 14)]

class Ifa_Ifu(Union):
    _fields_ = [('ifu_broadaddr', POINTER(Sockaddr)),
                ('ifu_dstaddr', POINTER(Sockaddr))]

class Ifaddrs(Structure):
    pass

Ifaddrs._fields_ = [('ifa_next', POINTER(Ifaddrs)), ('ifa_name', c_char_p),
                    ('ifa_flags', c_uint), ('ifa_addr', POINTER(Sockaddr)),
                    ('ifa_netmask', POINTER(Sockaddr)), ('ifa_ifu', Ifa_Ifu),
                    ('ifa_data', c_void_p)]

#Function To List Available USB Ports
def serial_ports():
    get_LANstatus()
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
	    if 'USB' in port:
            	result.append(port)
        except (OSError, serial.SerialException):
            pass
    if not result:
        print("No serial devices connected")
	with open("output.txt", "a") as f:
    		f.write("Build Failed-No serial devices connected\nConnect and try")
        sys.exit()
    return result


usbList = serial_ports()
iname = get_interfaces()
usbIndex = 0
while usbIndex < len(usbList):

	currentUSB = usbList[usbIndex]
	usbIndex += 1
	initifCommand = 'sudo ifconfig {iname} 192.168.1.25 netmask 255.255.255.0'.format(iname=iname)
	#p = os.popen('sudo -S %s'%(sudoCommand),'w').write(sudoPassword)
	r = os.popen(initifCommand)

	console = serial.Serial(port=currentUSB,baudrate=115200,parity="N",stopbits=1,bytesize=8,timeout=8)

	if not console.isOpen():
		sys.exit()

	console.flushInput()

	print(console.name)
	console.write("\n".encode())
	time.sleep(5)

	interruptRead = console.inWaiting()
	time.sleep(.5)

	while interruptRead < console.inWaiting():
	    interruptRead = console.inWaiting()
	    time.sleep(1)

	interruptData = console.read(interruptRead).decode('utf-8')
	print(interruptData.encode('utf-8'))

	console.write("reboot".encode())
	console.write("\n".encode())
	time.sleep(20)

	rebootRead = console.inWaiting()
	time.sleep(.5)

	while rebootRead < console.inWaiting():
	    rebootRead = console.inWaiting()
	    time.sleep(1)

	rebootData = console.read(rebootRead).decode('utf-8')
	print(rebootData.encode('utf-8'))

	loopcount = 20

	while loopcount > 10:
	     loopcount = loopcount - 1
	     console.write("\n".encode())
	     time.sleep(2)

	bootInterruptRead = console.inWaiting()
	time.sleep(.5)

	while bootInterruptRead < console.inWaiting():
	    bootInterruptRead = console.inWaiting()
	    time.sleep(1)

	bootInterruptData = console.read(bootInterruptRead).decode('utf-8')
	print(bootInterruptData.encode('utf-8'))

	console.write("setenv bootcmd bootcalix".encode())
	console.write("\n".encode())
	time.sleep(2)

	console.write("setenv ipaddr 192.168.1.1".encode())
	console.write("\n".encode())
	time.sleep(2)

	console.write("setenv serverip 192.168.1.25".encode())
	console.write("\n".encode())
	time.sleep(2)

	console.write("save".encode())
	console.write("\n".encode())
	time.sleep(2) 

	console.close()

	sudoCommand = 'nmcli con down id "Wired connection 1"'
	#p = os.popen('sudo -S %s'%(sudoCommand),'w').write(sudoPassword)
	p = os.popen(sudoCommand)
	time.sleep(5) 

	ifconfCommand = 'sudo ifconfig {iname} 192.168.1.25 netmask 255.255.255.0'.format(iname=iname)
	#p = os.popen('sudo -S %s'%(sudoCommand),'w').write(sudoPassword)
	q = os.popen(ifconfCommand)
	time.sleep(5) 

	console = serial.Serial(port=currentUSB,baudrate=115200,parity="N",stopbits=1,bytesize=8,timeout=8)

	if not console.isOpen():
		sys.exit()

	console.flushInput()

	print(console.name)
	time.sleep(2)

	userInput = sys.argv[1]
	if userInput == "upgrade":
		if len(os.listdir('/tftpboot/upgrade/') ) == 0:
			get_image_from_server("upgrade/")
		time.sleep(2)
		filename = os.listdir("/tftpboot/upgrade/")
		filename = filename[0]
    		console.write("upgclximg /tftpboot/upgrade/"+filename.encode())
		console.write("\n".encode())
		time.sleep(2)
	elif userInput == "downgrade":
		if len(os.listdir('/tftpboot/downgrade/') ) == 0:
			get_image_from_server("downgrade/")
		time.sleep(2)
		filename = os.listdir("/tftpboot/downgrade/")
		filename = filename[0]
    		console.write("upgclximg /tftpboot/downgrade/"+filename.encode())
		console.write("\n".encode())
		time.sleep(2)

	environmentRead = console.inWaiting()
	time.sleep(.5)

	while environmentRead < console.inWaiting():
	    environmentRead = console.inWaiting()
	    time.sleep(1)
	environmentData = console.read(environmentRead).decode('utf-8')
	print(environmentData.encode('utf-8'))
	console.flushInput()

	while 1:
	#  print("Reading")
	  environmentRead = console.inWaiting()
	  time.sleep(.5)
	  while environmentRead < console.inWaiting():
	      environmentRead = console.inWaiting()
	      time.sleep(1)          # Wait forever for anything
	  environmentData = console.read(environmentRead).decode('utf-8')
	  print(environmentData.encode('utf-8'))
	  if 'Flashing success!' in environmentData.encode('utf-8'):
		print("Found Success")
		with open("output.txt", "a") as f:
    			f.write("\nFlashed successfully")
		break
	  console.flushInput()

	print("Flash Complete")

	console.write("reset".encode())
	console.write("\n".encode())
	time.sleep(2)

	finishFlashRead = console.inWaiting()
	time.sleep(.5)

	while finishFlashRead < console.inWaiting():
	    finishFlashRead = console.inWaiting()
	    time.sleep(1)

	finishFlashData = console.read(finishFlashRead).decode('utf-8')
	print(finishFlashData.encode('utf-8'))

	console.close()
