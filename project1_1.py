import socket as skt 
import requests
import sys
import time
import os
from urlparse import urlparse


def make_request(url, path):
	NL = "\r\n"
	return ("GET {p} HTTP/1.1" + NL
		+"Host: {h}"+NL +NL). format(p=path,u=url)


def Main():
	link = sys.argv[-1]
	FILENAME = sys.argv[-2]
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
			clientSocket.connect(URL, parseStr.PORT)
		clientSocket.send(request)
		print 'Connected......'
		lists = []

	except skt.error as serr:
		print ("Error.....", serr)
	# = open("newfile.txt", "w")

	data_recieved = clientSocket.recv(1024)
	bytes_rec = 0
	index = data_recieved.find('\r\n\r\n')
	data_no_header = data_recieved[index+4:]
	bytes_rec +=len(data_recieved)

	file = open(FILENAME, 'wb')
	file.write(data_no_header)
	while True:
		data_recieved = clientSocket.recv(1024)
		if not data_recieved:
			break
			bytes_rec += len(data_recieved)
			file.write(data_recieved)
	clientSocket.close()

	print "completed"
	clientSocket.close()




if __name__ == '__main__':
	Main()
