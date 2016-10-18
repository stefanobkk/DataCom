#!/usr/bin/env python
import socket as skt 
import requests
import sys
import time
import os
import asyncore
import logging
from urlparse import urlparse


def make_request(url, path):
	NL = "\r\n"
	return ("GET {p} HTTP/1.1" + NL
		+"Host: {u}"+NL +NL).format(p=path,u=url)


def make_resume_req(path,host,obj,byte):
	NL = '\r\n'
	return ("GET {p} HTTP/1.1" 
		+ NL +"Host: {h}" 
		+ NL +"Connection: close"
		+ NL +"Range: {b}"+NL+NL).format(p=path,o=obj,h=host,b=byte)


def progess(bytes_so_far, chunk_size, total_size, start):
	total = time.time() - start
	percent = float(bytes_so_far)/total_size
	percent = round(percent*100, 2)
	aa = int((total_size/chunk_size)/total)
	sys.stdout.write("Downloaded %d of %d bytes (%.2f%%) \r" %(bytes_so_far, total_size, percent))
	if bytes_so_far >= total_size:
		sys.stdout.write('\n')
	return percent


def Main():

	if len(sys.argv) == 4:
		Filename_split = sys.argv[-2].split('.')
		File_name = Filename_split[0]
		File_extention = Filename_split[1]
		url = sys.argv[3]
		start_time = time.time()
		buffer_size = 1024

		if url[:7] != "http://":
			print "Please add http:// in the url name"
			sys.exit(1)
		if not os.path.isfile(File_name+".temp."+File_extention):
			print "Downloading your file"
			downloads(start_time, buffer_size, File_name, File_extention)
		else:
			print "Resuming your download"
			resume(start_time, buffer_size, File_name, File_extention)
	else: 
		print "Unreconnized command. Please input the correct command"
		print "python checkpoint2.py -o tt.txt http://speedtest.ftp.otenet.gr/files/test1Mb.db"
	print "File has been downloaded"


def file_content_extractor(header, filename, extention):
	Etag = ""
	Date_Modified = ""
	Content_length = ""
	Byte_recieved = ""
	with open(filename, 'wb') as file:
		for x in header[header.find('ETag:'): ]:
			if x == '\r':
				break
			Etag +=x
		for x in header[header.find('Content-Length:'):]:
			if x =='\r':
				break
			Content_length +=x
		for x in header[header.find('Last-Modified:'):]:
			if x =='\r':
				break
			Date_Modified +=x
		for x in header[header.find('Byte-recieved:'):]:
			if x =='\r':
				break
			Byte_recieved +=x
	file.close()
	return Etag, Date_Modified, Content_length, Byte_recieved


def head_Runner(clientSocket):
	result = ""	
	header = ""
	while "\r\n\r\n" not in header:
		result = clientSocket.recv(1)
		header += result
	return header


def downloads(start_time, buffer_size, filename, extention):
	Etag = ""
	Date_Modified = ""
	Content_length = ""
	byte_recieved = 0
	temp_file_size = 0 
	full_http_link = sys.argv[-1]
	parseStr = urlparse(full_http_link)
	URL = parseStr.hostname
	PATH = parseStr.path
	PORT = parseStr.port
	temp_file = open(filename+".temp."+extention, 'wb')

	try:
		print "Attempting to establish a connection"
		request = make_request(URL, PATH)
		clientSocket = skt.socket(skt.AF_INET, skt.SOCK_STREAM)
		if parseStr.port == None:
			url3 = URL.find("/")
			clientSocket.connect((URL, 80))
		else:
			url3 = URL.find(":")
			clientSocket.connect(full_http_link, parseStr.PORT)
		clientSocket.send(request)
	except skt.error as serr:
		clientSocket.close()
		print "Error could not establish a connection", serr
	print "\nConnection has been established ready to start working......"


	header = head_Runner(clientSocket)
	with open(filename+"."+extention, 'wb') as file:
		myfile = file_content_extractor(header,filename, extention)
		Etag = myfile[0]
		Date_Modified = myfile[1]
		Content_length = myfile[2]
		counter = 0
		while True and counter <1000:
			counter +=1
			data_recieved = clientSocket.recv(buffer_size)
			if not data_recieved:
				break
			file.write(data_recieved)
			byte_recieved +=len(data_recieved)
			Content_length_int = int(Content_length.split(": ")[1])
			if byte_recieved <= Content_length_int:
				progess(byte_recieved, buffer_size, Content_length_int,start_time)

		byte_recieved_str = "Byte-recieved: " + str(byte_recieved)
		NL = '\r\n'
		temp_file.write(Etag + NL + Content_length + NL+  byte_recieved_str + NL+ Date_Modified)
	clientSocket.close()


def resume(start_time, buffer_size, filename, extention):
	byte_recieved = 0
	temp_file_size = 0 
	full_http_link = sys.argv[-1]
	parseStr = urlparse(full_http_link)
	URL = parseStr.hostname
	PATH = parseStr.path
	PORT = parseStr.port

	temp_file = open(filename+".temp."+extention, 'r').read()
	temp_file = temp_file.split("\r\n")

	Etag = temp_file[0].split(": ")[1]
	Content_length = temp_file[1].split(": ")[1]
	Byte_recieved = temp_file[2].split(": ")[1]
	Date_Modified = temp_file[3].split(": ")[1]

	try:
		print "Attempting to establish a connection"
		clientSocket = skt.socket(skt.AF_INET, skt.SOCK_STREAM)
		request_2 = make_resume_req(PATH, URL, '/', "bytes="+str(Byte_recieved)+"-")
		if parseStr.port == None:
			url3 = URL.find("/")
			clientSocket.connect((URL, 80))
		else:
			url3 = URL.find(":")
			clientSocket.connect(full_http_link, parseStr.PORT)
		clientSocket.send(request_2)
	except skt.error as serr:
		clientSocket.close()
		print "Error could not establish a connection", serr
	print "\nConnection has been established ready to start working......"

	header = head_Runner(clientSocket)
	current_byte_num = int(Byte_recieved)
	Content_length_num = int(Content_length)
	try:
		with open(filename+"."+extention, 'a+') as file: 
			counter = 0
			while True:
				data_recieved = clientSocket.recv(1024)
				if not data_recieved:
					break
				file.write(data_recieved)
				current_byte_num +=len(data_recieved)
				if byte_recieved <= Content_length:
					progess(current_byte_num, buffer_size, Content_length_num,start_time)
				counter+=1
	except IOError:
		raise
		sys.exit(1)
	except skt.timeout:
 		print("timeout error")
 		sys.exit(1)
 	except skt.error:
 		print("socket error occured: ")
 		sys.exit(1)
 	finally:
 		NL ="\r\n"
		with open(filename+".temp."+extention, 'wb') as file:
			current_byte_str = "Byte-recieved: " + str(current_byte_num)
			Etag = "ETag: "+ str(Etag)
			Content_length = "Content-Length: " + str(Content_length)
			Date_Modified = "Last-Modified: " + str(Date_Modified)
			file.write(Etag + NL + Content_length + NL + current_byte_str + NL + Date_Modified)
		if int(current_byte_num) == Content_length_num:
			os.remove(filename+".temp."+extention)
			print "Download complete"
	clientSocket.close()

if __name__ == '__main__':
	Main()

