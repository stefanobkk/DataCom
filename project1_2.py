#!/usr/bin/env python
import socket as skt
import os
import sys
from urlparse import urlparse

class Downloader(object):
    def __init__(self, url, path, filename, port):
        print 'mmmmmmmm'
        self.url = url
        self.path = path
        self.filename = filename
        self.port = port
        self.header = ""
        self.headerLength = 0
        self.content = ""
        self.contentLength = ""
        self.contentExist = False
        self.file = open(filename, "wb")
        self.clientSocket = skt.socket(skt.AF_INET, skt.SOCK_STREAM)
        self.checkResume = False
        self.headByte = 0
        self.tailByte = 0
        self.main()

    def urlVerification(self):
        if self.url[:7] != "http://":
            print "----", self.url[:7]
        return self.url


    def makeGet(self):
        print self.path
        return ("GET {n} HTTP/1.1\r\n"+ "Host: {s}\r\n"+"Connection: close\r\n\r\n").format(n=self.path,s=self.url)

    def Openconnection(self):
        self.clientSocket.connect((self.url, self.port))
        self.clientSocket.send(self.makeGet())

    def closeConnection(self):

        self.clientSocket.close()
        self.content = ""

    def makeHeader(self):
        self.Openconnection()
        while "\r\n\r\n" not in self.header:
            data = self.clientSocket.recv(1)
            self.header += data
            if "\r\n\r\n" in self.header:
                for x in self.header[self.header.find("Content-Length")+16:]:
                    if x =="\r":
                        self.contentExist = True
                        break
                    self.contentLength += x

        self.headerLength = len(self.header)


    def checkContent(self):
        return self.contentExist

    def downloadWithContent(self):

        while True:
            data = self.clientSocket.recv(1024)
            self.content += data
            if not data:
                break
        self.file.write(self.content)
        self.closeConnection()

    def downloadWithoutContent(self):
        while True:
            data = self.clientSocket.recv(1024)
            self.content += data
            if not data:
                break
        self.file.write(self.content)
        self.closeConnection()


    def checkTypeResume(self):
        return self.checkResume

    def resumeDownload(self):
        pass



    def checkPort(self):
        if self.port == None:
            self.port = 80

    def main(self):
        print "ppppp"
        self.urlVerification()
        #print self.urlVerification()
        self.checkPort()
        self.makeHeader()

        if self.checkTypeResume() == True:
            if self.checkContent() == True:
                self.downloadWithContent()
            if self.checkContent() == False:
                self.downloadWithoutContent()
        if self.checkTypeResume() == False:
            if self.checkContent() == True:
                self.downloadWithContent()
            if self.checkContent == False:
                self.downloadWithoutContent()





print "ooooo"
link = sys.argv[-1]
FILENAME = sys.argv[-2]
parseStr = urlparse(link)
URL = parseStr.hostname
PATH = parseStr.path
PORT = parseStr.port

a = Downloader(URL, PATH, FILENAME, PORT)