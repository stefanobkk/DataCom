#!/usr/bin/env python

import socket as skt 
import requests
import sys
import time
import os
from urlparse import urlparse


def make_request(url, path):
	NL = "\r\n"
	return ("GET {p} HTTP/1.1" + NL
		+"Host: {u}"+NL +NL).format(p=path,u=url)


def make_resume_req(path,host,obj,_byte):
	NL = '\r\n'
	return ("GET {p} HTTP/1.1" 
		+ NL +"Host: {h}" 
		+ NL +"Connection: close"
		+ NL +"Range: {b}"+NL+NL).format(p=path,o=obj,h=host,b=_byte)


#progress(byte_recieved, buffer_size, Content_length,start_time)
def progess(bytes_so_far, chunk_size, total_size, start):
	total = time.time() - start
	percent = float(bytes_so_far)/total_size
	percent = round(percent*100, 2)
	aa = int((total_size/chunk_size)/total)
	sys.stdout.write("Downloaded %d of %d bytes (%.2f%%)\r" %(bytes_so_far, total_size, percent))
	if bytes_so_far >= total_size:
		sys.stdout.write('\n')
	return percent


def Main():
	Filename = sys.argv[-2]
	Filename_split = sys.argv[-2].split('.')
	Filename = Filename_split[0]
	File_extention = Filename_split[1]
	url = sys.argv[3]

	start_time = time.time()
	buffer_size = 1024

	if len(sys.argv) <4:
		print "You need to enter the correct command."
		print "Example --> " + "srget -o filename.txt http://url/"
		sys.exit(1)

	if url[:7] != "http://":
		print "Please add http:// in the url name"
		sys.exit(1)

	if not os.path.isfile(Filename+".temp."+File_extention):
		print "Downloading your file"
		downloads(start_time,buffer_size)
	else:
		print "Resuming your download"
		resume(start_time, buffer_size)


def downloads(start_time, buffer_size):
	link = sys.argv[-1]
	FILENAME = sys.argv[-2]
	File_name = FILENAME.split(".")
	parseStr = urlparse(link)
	URL = parseStr.hostname
	PATH = parseStr.path
	PORT = parseStr.port

	#make a connection
	try:
		request = make_request(URL, PATH)
		clientSocket = skt.socket(skt.AF_INET, skt.SOCK_STREAM)
		#clientSocket.settimeout(5)
		if parseStr.port == None:
			url3 = URL.find("/")
			clientSocket.connect((URL, 80))
		else:
			url3 = URL.find(":")
			clientSocket.connect(link, parseStr.PORT)
		clientSocket.send(request)
		#clientSocket.settimeout(None)
		print 'Connected to socket......'

	except skt.error as serr:
		clientSocket.close()
		print "Error.....", serr

	##Getting the header of the file

	result = ""	
	header = ""
	while "\r\n\r\n" not in header:
		result = clientSocket.recv(1)
		header += result



	byte_recieved = 0
	counter = 0

	#Creating a temporary file
	temp_file = open(File_name[0]+".temp."+"txt", 'wb')
	tmp_file_size = 0
	#try:
	with open(FILENAME, 'wb') as file: 
		#Extracting header and putting it into a temporaty file so we can check during resume. 
		Etag = ""
		Date_Modified = ""
		Content_length = ""
		for x in header[header.find('ETag:'): ]:
			if x == '\r':
				break
			Etag +=x


		for x in header[header.find('Content-Length:'):]:
			if x =='\r':
				break
			Content_length +=x

		Content_length_int = Content_length.split(": ")[1]
		Content_length_int = int(Content_length_int)


		for x in header[header.find('Last-Modified:'):]:
			if x =='\r':
				break
			Date_Modified +=x

		counter =0 
		while True and counter <10:
			data_recieved = clientSocket.recv(buffer_size)
			if not data_recieved:
				break
			file.write(data_recieved)
			byte_recieved +=len(data_recieved)
			if byte_recieved <= Content_length:
				progess(byte_recieved, buffer_size, Content_length_int,start_time)
			counter+=1

		byte_recieved_str = "Byte-recieved: " + str(byte_recieved)


		#Here we write the content into our temporary file
		NL = '\r\n'
		temp_file.write(Etag + NL + Content_length + NL+  byte_recieved_str + NL+ Date_Modified)


	if Content_length_int == byte_recieved:
		print "You have downloaded your file of size", byte_recieved
		os.remove(File_name[0]+".temp."+File_name[1])

	clientSocket.close()




def resume(start_time, buffer_size):
	link = sys.argv[-1]
	FILENAME = sys.argv[-2]
	File_name = FILENAME.split(".")
	parseStr = urlparse(link)
	URL = parseStr.hostname
	PATH = parseStr.path
	PORT = parseStr.port

	#Pulling all the content from our temporary file that contains the header. 
	ETag = ""
	Content_length = ""
	byte_recieved =""
	Date_Modified = ""


	#Here we open the temporary file and extract all the content from it.
	temp_file = open(File_name[0]+".temp."+File_name[1], 'r').read() #open our temporary file and .read() turns it into a string
	for x in temp_file[temp_file.find('ETag:'):]:
		if x =='\r':
			break
		ETag += x
	ETag_split = ETag.split(': ')

	for x in temp_file[temp_file.find('Content-Length:'):]:
		if x =='\r':
			break
		Content_length +=x
	Content_length_split = Content_length.split(': ')


	for x in temp_file[temp_file.find('Last-Modified:'):]:
		if x =='\r':
			break
		Date_Modified +=x
	Date_Modified_split = Date_Modified.split(': ')

	for x in temp_file[temp_file.find('Byte-recieved:'):]:
		if x =='\r':
			break
		byte_recieved +=x
	byte_recieved_split = byte_recieved.split(': ')


	#Try to make a connection
	try:
		request_2 = make_resume_req(PATH, URL, '/', "bytes="+str(byte_recieved_split[1])+"-") #Our new HTTP Get 
		clientSocket = skt.socket(skt.AF_INET, skt.SOCK_STREAM)
		if parseStr.port == None:
			url3 = URL.find("/")
			clientSocket.connect((URL, 80))
		else:
			url3 = URL.find(":")
			clientSocket.connect(link, parseStr.PORT)
		clientSocket.send(request_2)
		print 'Connected......'
	except skt.error as serr:
		print ("Error.....", serr)


	##Getting the header of the file
	header2 = ""
	result2 = ""
	while "\r\n\r\n" not in header2:
		result2 = clientSocket.recv(1)
		header2 += result2
	counter = 0
	current_byte_num = int(byte_recieved_split[1])
	temp_file = open(File_name[0]+".temp."+File_name[1], 'wb')


	Content_length_int = Content_length.split(": ")[1]
	Content_length_int = int(Content_length_int)


	#These are variables for the percentage counter
	aa = progess(current_byte_num, buffer_size, Content_length_int,start_time)
	aa = str(aa)
	bb = aa.split(" (")
	print "Downloading from %s percent and at %s bytes" %(bb[0], current_byte_num)
	
	try:
		with open(FILENAME, 'a+') as file: 
			while True:
				data_recieved = clientSocket.recv(1024)
				if not data_recieved:
					break
				file.write(data_recieved)
				current_byte_num +=len(data_recieved)
				if byte_recieved <= Content_length:
					progess(current_byte_num, buffer_size, Content_length_int,start_time)
				#counter+=1
	except IOError:
		raise
		#with open(File_name[0]+".temp."+File_name[1], 'wb') as file:
		#	file.write(ETag + NL + Content_length + NL + current_byte_str + NL + Date_Modified + NL)
		sys.exit(1)

	finally:
		NL ="\r\n"
		with open(File_name[0]+".temp."+File_name[1], 'wb') as file:
			current_byte_str = "Byte-recieved: " + str(current_byte_num)
			file.write(ETag + NL + Content_length + NL + current_byte_str + NL + Date_Modified + NL)
		if int(current_byte_num) == Content_length_int:
			os.remove(File_name[0]+".temp."+File_name[1])
			print "Donwload complete"

		else:
			print "Part of the file is missing. Please resume the download."

	#current_byte_num2 = current_byte_num
	#current_byte_num = "Byte-recieved: " + str(current_byte_num)

	#Here we write the content back into our temporary file. 
	#NL = '\r\n'
	#temp_file.write(ETag + NL + Content_length + NL + current_byte_num + NL + Date_Modified)


	#print current_byte_num2
	#print Content_length_int

	#Check to see if the data we have recieved is eqaul to the content length. 
	
	#if current_byte_num2 == Content_length_int and os.path.isfile(File_name[0]+".temp."+File_name[1]):
	#	print "Download Complete "
	#	os.remove(File_name[0]+".temp."+File_name[1])
	clientSocket.close()



if __name__ == '__main__':
	Main()
