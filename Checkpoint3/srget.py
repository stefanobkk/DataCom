#!/usr/bin/env python
import socket as skt 
import requests
import sys
import time
import os
import asyncore
import logging
from urlparse import urlparse
import threading
import itertools


def make_request(url, path):
	NL = "\r\n"
	return ("GET {p} HTTP/1.1" + NL
		+"Host: {u}"+NL 
		+"Connection: close" + NL
		+ NL).format(p=path,u=url)


def make_resume_req(path,host,obj,byte):
	NL = '\r\n'
	return ("GET {p} HTTP/1.1" 
		+ NL +"Host: {h}" 
		+ NL +"Connection: close"
		+ NL +"Range: {b}"+NL+NL).format(p=path,o=obj,h=host,b=byte)



def content_extractor(url):
	parseStr = urlparse(url)
	host_name = parseStr.hostname
	port = parseStr.port
	path = parseStr.path
	return host_name, port, path


def header_extractor(clientSocket):
	result = ""
	header = ""
	while "\r\n\r\n" not in header:
		result = clientSocket.recv(1)
		header += result
	return header


def content_length_extractor(url):
	host_name, port, path = content_extractor(url)
	clientSocket = skt.socket(skt.AF_INET, skt.SOCK_STREAM)
	if not port:
		clientSocket.connect((host_name, 80))
		request_no_range = make_request(host_name, path)
	else:
		clientSocket.connect((host_name, port))
		request_no_range = make_request(host_name, path)
	clientSocket.send(request_no_range)
	print request_no_range
	header = header_extractor(clientSocket)
	L_slice = header[header.find("Content-Length: "):]


	content_length = ""
	for x in header[header.find('Content-Length:'):]:
		if x =='\r':
			break
		content_length +=x
	return content_length


def download_error_checker(thread_status_list, content_length):
	counter = 0 
	for i in thread_status_list:
		if i == False:
			print "There was an error whilst downloading chunk number", counter
		else: 
			print "we are in another loop. "
		counter +=1


#In this function we are just preparing our file to be downloaded concurrently.
def download_preparation(filename_split_list, content_length, content_range, connection_number, thread_status_list, url):
	cc = (int(content_range[1]) - int(content_range[0])) +1
	size_of_each_chunk = int(content_length.split(": ")[1]) / connection_number
	chunk_divider_table = [None] * connection_number
	

	all_points = []
	all_points = [content_range[0]] + all_points
	for x in range(connection_number):
		if x > 0:
			starter = size_of_each_chunk * x
			ender = (starter - 1)
			all_points.append(ender)
			all_points.append(starter)
	all_points = all_points + [content_range[1]]

	for i in all_points:
		starting_only = all_points[::2]
		ending_only = all_points[1::2]


	combined_start_end_list = []
	for i, j in zip(starting_only, ending_only):
		combined_start_end_list.append([i,j])

	chunk_divider_table = [None] * connection_number
	result_range = []

	try:
		for i, j, k in zip(result_range, range(connection_number), thread_status_list):
			t = threading.Thread(target=thread_allocator, args=(
				cc, size_of_each_chunk, filename_split_list, 
				url, i, connection_number, thread_status_list))
			t.start()
	
	except Exception:
		print "Something went really wrong"
		print Exception



	print "starting, ending", starting_only, ending_only
	print combined_start_end_list


def create_meta_files(filename, connection_number):
	print "In create meta files"
	filenames = [] 
	for i in range(connection_number):
		tmp = filename[0] + "_meta" + str(i)
		filenames.append(tmp)
	return filenames


def thread_allocator(starting_points_only, ending_points_only, content_length, size_of_each_chunk, 
	filename_split_list, url, i, connection_number, thread_status_list):

	print "In thread allocator"
	metadata_filenames = create_meta_files(filename_split_list, connection_number)
	print metadata_filenames


	#for i, j, k, l in zip(metadata_filenames, starting_points_only, ending_points_only, range(len(thread_status_list))):
		#t = threading.Thread(target = downloader, args=(
	#		str(i)))



	#print size_of_each_chunk

def Main():
	Filename_split_list = sys.argv[-2].split('.')
	url = sys.argv[-1]
	start_time = time.time()
	buffer_size = 1024
	content_length = content_length_extractor(sys.argv[-1])
	content_range = [0, content_length.split(": ")[1]]
	connection_number = 6
	thread_status_list = [None] * connection_number
	print content_range


	#So if the file has not been downlaoded yet we passs the whole content range in so that our downloader
	# function can break it down into smaller pieces and then send it to the thread to prepare its executon. 
	download_preparation(Filename_split_list, content_length, content_range, connection_number, thread_status_list, url)


	#Resume thread --> Thread Allocator --> part Doanloader





if __name__ == '__main__':
	Main()
