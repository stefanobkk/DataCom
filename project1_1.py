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


def make_resume_req(host,obj,_byte):
	NL = '\r\n'
	return ("GET {o} HTTP/1.1" 
		+ NL +"Host: {h}" 
		+ NL +"Connection: close"
		+ NL +"Range: {b}\r\n").format(o=obj,h=host,b=_byte)

def Main():
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


	#Extra information about the file. Alternative to the one above.
	response_url = requests.get(link, stream=True)
	total_length = response_url.headers.get('content-length')
	total_length_int = float(total_length)

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
		header = header + byte_recieved_str
		#temp_file.write(header)

		Etag = " "
		for x in header[header.find('ETag:'): ]:
			if x == '\r':
				break
			Etag +=x

		Content_length = " "
		for x in header[header.find('Content-Length:'):]:
			if x =='\r':
				break
			Content_length +=x

		recieved = " "
		for x in header[header.find('Byte-recieved:'):]:
			if x =='\r':
				break
			recieved +=x

		Date_Modified = " "
		for x in header[header.find('Last-Modified:'):]:
			if x =='\r':
				break
			Date_Modified +=x

		NL = '\r\n'
		temp_file.write(Etag + NL + Content_length + NL+ recieved + NL+ Date_Modified)






	#Find size of the temp file and check if there is anythng inside it
	#	if there is something inside then we enter resume()
	#	else enter new Download()	



	#request_2 = make_resume_req(URL,'/',byte_recieved)


	#print request_2
	print byte_recieved, " Bytes received"
	print "completed"
	clientSocket.close()







if __name__ == '__main__':
	Main()
