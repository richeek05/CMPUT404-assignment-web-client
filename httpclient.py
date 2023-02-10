#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it


import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):

    def get_host_port(self,url):
        # parse the url to get the hostname and port
        # reference: https://docs.python.org/3/library/urllib.parse.html
        after_parsing = urllib.parse.urlparse(url)
        port = after_parsing.port
        host = after_parsing.hostname
        if port == None:
            return host,80
        else:
            return host, port


    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    # Code is the second thing returned in the first line, Eg: "HTTP/1.1 301 Moved Permanently\r\n"
    def get_code(self, data):
        line = data.split("\r\n")[0]
        code = int(line.split(" ")[1])
        return code

    # Headers is the content being returned till '\r\n\r\n'
    def get_headers(self,data):
        headers = data.split('\r\n\r\n')[0]
        return headers

    # Body is the content returned after '\r\n\r\n'
    def get_body(self, data):
        body = data.split('\r\n\r\n')[1]
        return body
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')


    # reference: https://docs.python.org/3/library/socket.html
    def GET(self, url, args=None):
        #code = 500
        #body = ""
        
        # get the hostname and port using the get_host_port() function
        host, port  = self.get_host_port(url)

        # get the path using urlib.parse 
        path = urllib.parse.urlparse(url).path
        if not path:
            path = '/'

        self.connect(host,port)
        # reference: https://uofa-cmput404.github.io/cmput404-slides/04-HTTP.html#
        request = f"GET {path} HTTP/1.1\r\nHost: {host}\r\nAccept: */*\r\nConnection: close\r\n\r\n"

        # send the request
        self.sendall(request)

        recvall = self.recvall(self.socket)

        # get Headers, Code and Body from recvall(reading it from socket)
        headers = self.get_headers(recvall)
        code = self.get_code(recvall)
        body = self.get_body(recvall)

        print(f"\nHeaders: {headers} \nCode: {code} \nBody: {body}")        
        
        self.close()
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        #code = 500
        #body = ""
        
        # get the hostname and port using the get_host_port() function
        host, port  = self.get_host_port(url)

        # get the path using urlib.parse 
        path = urllib.parse.urlparse(url).path
        if not path:
            path = '/'

        if args != None:
            args = urllib.parse.urlencode(args)
        else:
            args = ""

        self.connect(host,port)
        
        args_len = str(len(args))

        # reference: https://uofa-cmput404.github.io/cmput404-slides/04-HTTP.html#/30
        request = f"POST {path} HTTP/1.1\r\nHost: {host}\r\nAccept: */*\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: {args_len}\r\nConnection: close\r\n\r\n{args}"

        # send the request
        self.sendall(request)

        recvall = self.recvall(self.socket)

        # get Headers, Code and Body from recvall(reading it from socket)
        headers = self.get_headers(recvall)
        code = self.get_code(recvall)
        body = self.get_body(recvall)

        print(f"\nHeaders: {headers} \nCode: {code} \nBody: {body}") 

        self.close()
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
