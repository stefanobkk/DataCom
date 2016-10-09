
import requests
import sys
import urllib2
import time

def make_request(url):
	NL = "\r\n"
	print "new requestisssss........"
	return ("GET /HTTP/1.1" +NL +
		"Host:{urls}" +NL +
		"Connection: keep-alive" + NL +
		"Upgrade-Insecure-Requests: 1"+ NL +
		NL).format(urls = url)



def speedTest(start, size, text, file_name):
	total = time.clock() - start
	print "%s reading took %d seconds, transfer rate %.2f KBPS" %(text, total, (size/1024.0)/ total)
	print "Page/File size: %sKB" %(size)
	print "Saving file to: %s" %(file_name)

def Main():
	#url = "http://pantip.com"
	user_filename = sys.argv[0]
	action = sys.argv[1]
	new_file_name = sys.argv[2]
	website_url = sys.argv[3]

	aa = make_request(website_url)
	print aa


	#Chuncked
	f = urllib2.urlopen(website_url)
	start_time = time.clock()
	data = []
	chunk = f.read(1024)
	while chunk:
		data.append(chunk)
		chunk = f.read(1024)
		print chunk
		if not chunk:
			break 
	speedTest(start_time, len(data), 'Chuncked', new_file_name)
	f.close() 


if __name__ == '__main__':
	Main()