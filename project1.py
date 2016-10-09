
import requests
import sys
import urllib2
import time
import socket as skt 
from time import sleep
import sys


def speedTest(start, size, file_name):
	total = time.time() - start
	print "Reading took %.2f seconds, transfer rate %.2f KBPS" %(total, (size/1024.0)/ total)

def progess(bytes_so_far, chunk_size, total_size):
	percent = float(bytes_so_far)/total_size
	percent = round(percent*100, 2)
	sys.stdout.write("Downloaded %d of %d bytes (%.2f%%)\r" %(bytes_so_far, total_size, percent))

	if bytes_so_far >= total_size:
		sys.stdout.write('\n')

def Main():
	user_filename = sys.argv[0]
	action = sys.argv[1]
	new_file_name = sys.argv[2]
	website_url = sys.argv[3]

	chunk_size = 1024
	data = []
	start_time = time.time()

	response = requests.get(website_url, stream=True)
	total_length = response.headers.get('content-length')
	total_length_int = float(total_length)
	print "Total download size: %.2fKB" %(total_length_int/chunk_size)

	f = urllib2.urlopen(website_url)
	chunk = f.read(chunk_size)
	bytes_so_far = 0
	while chunk:
		data.append(chunk)
		chunk = f.read(chunk_size)
		bytes_so_far += len(chunk)
		if not chunk:
			break 
		if bytes_so_far<= total_length_int:
			progess(bytes_so_far, chunk_size, total_length_int)

	speedTest(start_time, total_length_int, new_file_name)
	f.close() 


if __name__ == '__main__':
	Main()


