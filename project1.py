
import requests
import sys
import urllib2
import time
import os
import socket as skt 


def make_http_request_3(host,obj ):
	NL = "\r\n"
	return ("GET {o} HTTP/1.1" +NL
		+ "Host: {s}" + NL
		+ "Connection: " 'Keep-Alive' + NL
		+ "Accept-Language: en-us" +NL
		+NL).format(o=obj,s=host)

def speedTest(start, size, file_name):
	total = time.time() - start
	print "Reading took %.2f seconds, transfer rate %.2f KBPS" %(total, (size/1024.0)/ total)

def progess(bytes_so_far, chunk_size, total_size, start, size, file_name):
	total = time.time() - start
	percent = float(bytes_so_far)/total_size
	percent = round(percent*100, 2)
	aa = int((size/chunk_size)/total)
	sys.stdout.write("Downloaded %d of %d bytes (%.2f%%) \r" %(bytes_so_far, total_size, percent))
	if bytes_so_far >= total_size:
		sys.stdout.write('\n')

def Main():
	user_filename = sys.argv[0]
	action = sys.argv[1]
	new_file_name = sys.argv[2]
	website_url = sys.argv[3]
	##Neeed Error handling here #####

	chunk_size = 1024
	data = []
	start_time = time.time()

	"""
	bb = make_http_request_3(host, '/')
	#print bb
	clientSocket = skt.socket(skt.AF_INET, skt.SOCK_STREAM)
	clientSocket.connect((host, port))
	clientSocket.send(bb)
	"""

	response_url = requests.get(website_url, stream=True)
	total_length = response_url.headers.get('content-length')
	total_length_int = float(total_length)

	print response_url.headers

	print "Total download size: %.2fKB" %(total_length_int/chunk_size)
	f = urllib2.urlopen(website_url)
	chunk = f.read(chunk_size)
	bytes_so_far = 0
	while chunk:
		#datarec = clientSocket.recv(1024)
		print chunk
		data.append(chunk)
		chunk = f.read(chunk_size)
		bytes_so_far += len(chunk)
		if not chunk:
			break 
		if bytes_so_far<= total_length_int:
			progess(bytes_so_far, chunk_size, total_length_int,start_time, total_length_int, new_file_name)

	time.sleep(3)
	speedTest(start_time, total_length_int, new_file_name)
	f.close() 


if __name__ == '__main__':
	Main()


