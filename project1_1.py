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
	return ("GET {o}{p} HTTP/1.1" 
		+ NL +"Host: {h}" 
		+ NL +"Connection: close"
		+ NL +"Range: {b}"+NL+NL).format(p=path,o=obj,h=host,b=_byte)


def Main():

	#downloads()
	resume()


def downloads():
	link = sys.argv[-1]
	FILENAME = sys.argv[-2]
	File_name = FILENAME.split(".")
	parseStr = urlparse(link)
	URL = parseStr.hostname
	PATH = parseStr.path
	PORT = parseStr.port

	try:
		request = make_request(URL, PATH)
		clientSocket = skt.socket(skt.AF_INET, skt.SOCK_STREAM)
		if parseStr.port == None:
			url3 = URL.find("/")
			clientSocket.connect((URL, 80))
		else:
			url3 = URL.find(":")
			clientSocket.connect(link, parseStr.PORT)
		print request
		clientSocket.send(request)
		print 'Connected......'

	except skt.error as serr:
		print ("Error.....", serr)


	##Getting the header of the file
	result = ""	
	header = ""
	while "\r\n\r\n" not in header:
		result = clientSocket.recv(1)
		header += result


	print request
	print header


	byte_recieved = 0
	counter = 0
	temp_file = open(File_name[0]+".temp."+"txt", 'wb')
	tmp_file_size = 0
	with open(FILENAME, 'wb') as file: 
		while True and counter<5:
			print "in a damn loop"
			data_recieved = clientSocket.recv(1024)
			if not data_recieved:
				break
			file.write(data_recieved)
			byte_recieved +=len(data_recieved)
			counter+=1


		## Adding bytes-recieved to the temp file
		byte_recieved_str = "Byte-recieved: " + str(byte_recieved)


		#Extracting header and putting it into a temporaty file so we can check during resume. 
		Etag = ""
		for x in header[header.find('ETag:'): ]:
			if x == '\r':
				break
			Etag +=x

		Content_length = ""
		for x in header[header.find('Content-Length:'):]:
			if x =='\r':
				break
			Content_length +=x
		
		Date_Modified = ""
		for x in header[header.find('Last-Modified:'):]:
			if x =='\r':
				break
			Date_Modified +=x
			#print Date_Modified.split[":"]


		NL = '\r\n'
		temp_file.write(Etag + NL + Content_length + NL+  byte_recieved_str + NL+ Date_Modified)


	#make_resume_req(URL, '/', byte_recieved)
	#print make_resume_req


	#Find size of the temp file and check if there is anythng inside it
	#	if there is something inside then we enter resume()
	#	else enter new Download()	


	print byte_recieved, " Bytes received"
	print "completed"
	clientSocket.close()


def resume():
	link = sys.argv[-1]
	FILENAME = sys.argv[-2]
	File_name = FILENAME.split(".")
	parseStr = urlparse(link)
	URL = parseStr.hostname
	PATH = parseStr.path
	PORT = parseStr.port
	

	temp_file = open(File_name[0]+".temp."+"txt", 'r').read()

	ETag = ""
	for x in temp_file[temp_file.find('ETag:'):]:
		if x =='\r':
			break
		ETag += x
	ETag = ETag.split(': ')

	Content_length = ""
	for x in temp_file[temp_file.find('Content-Length:'):]:
		if x =='\r':
			break
		Content_length +=x
	Content_length = Content_length.split(': ')

	Date_Modified = ""
	for x in temp_file[temp_file.find('Last-Modified:'):]:
		if x =='\r':
			break
		Date_Modified +=x
	Date_Modified = Date_Modified.split(': ')

	byte_recieved =""
	for x in temp_file[temp_file.find('Byte-recieved:'):]:
		if x =='\r':
			break
		byte_recieved +=x
	byte_recieved = byte_recieved.split(': ')


	request_2 = make_resume_req(PATH, URL, '/', "bytes="+str(byte_recieved[1])+"-")
	clientSocket = skt.socket(skt.AF_INET, skt.SOCK_STREAM)
	if parseStr.port == None:
		url3 = URL.find("/")
		clientSocket.connect((URL, 80))
	else:
		url3 = URL.find(":")
		clientSocket.connect(link, parseStr.PORT)
	clientSocket.send(request_2)
	print 'Connected......'

	header2 = ""
	result2 = ""

	while "\r\n\r\n" not in header2:
		result2 = clientSocket.recv(1)
		header2 += result2

	counter = 0
	current_byte_num = int(byte_recieved[1])
	temp_file = open(File_name[0]+".temp."+"txt", 'a+')
	with open(FILENAME, 'wb') as file: 
		while True and counter<9:
			print "in a damn loop"
			data_recieved = clientSocket.recv(1024)
			if not data_recieved:
				break
			file.write(data_recieved)
			current_byte_num +=len(data_recieved)
			counter+=1

	print "++++++++++",current_byte_num





	print request_2
	print header2
	clientSocket.close()


if __name__ == '__main__':
	Main()
