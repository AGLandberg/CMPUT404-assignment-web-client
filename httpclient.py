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

from ast import arguments
from asyncio.format_helpers import _format_args_and_kwargs
from importlib.resources import path
import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse
from wsgiref.headers import Headers
from time import sleep

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    def get_host_port(self,url):
        #parse the url in order to get the correct host and port values 
        urlTuple = urllib.parse.urlparse(url)
        host, port =  urlTuple.netloc.split(":") if ":" in urlTuple.netloc else \
                        (urlTuple.netloc, 80)
        return (host, int(port))

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        headers = self.get_headers(data)
        status_line = headers.split('\r\n')[0]
        code = status_line.split(' ')[1]
        return int(code)

    def get_headers(self,data):
        index = data.find('\r\n\r\n')
        return data[:index]

    def get_body(self, data):
        index = data.find('\r\n\r\n')
        if index >= 0:
            return data[index + 4:]
        return data
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    #get host information
    def get_remote_ip(self, host):
        print(f'Getting IP for {host}')
        try:
            remote_ip = socket.gethostbyname( host )
        except socket.gaierror:
            print ('Hostname could not be resolved. Exiting')
            sys.exit()

        print (f'Ip address of {host} is {remote_ip}')
        return remote_ip

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

    def build_path(self, url):
        urlTuple =urllib.parse.urlparse(url)
        path = urlTuple.path
        if urlTuple.params:
            path += ';' + urlTuple.params
        if urlTuple.query:
            path += '?' + urlTuple.query
        if urlTuple.fragment:
            path += '#' + urlTuple.fragment
        return path

    def GET(self, url, args=None):
        host, port = self.get_host_port(url)
        path = self.build_path(url)
        if not path:
            path = "/"
        data = f'GET {path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\nAccept: */*\r\n\r\n'
        print("*****REQUEST:", data)
        self.connect(self.get_remote_ip(host), port)
        self.sendall(data)
        response = self.recvall(self.socket)
        self.socket.close()
        code = self.get_code(response)
        body = self.get_body(response)
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        host, port = self.get_host_port(url)
        path = self.build_path(url)
        if not path:
            path = "/"

        body = ''
        content_length = 0
        if args:
            body = urllib.parse.urlencode(args)
            content_length = len(body.encode('utf-8'))

        data = f'POST {path} HTTP/1.1\r\nHost: {host}\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: {content_length}\r\nConnection: close\r\nAccept: */*\r\n\r\n{body}'
        print("*****REQUEST:", data)
        self.connect(self.get_remote_ip(host), port)
        self.sendall(data)
        response = self.recvall(self.socket)
        print("***RESPONSE ", response) 
        self.socket.close()
        code = self.get_code(response)
        body = self.get_body(response)
        return HTTPResponse(code, body)
    
    def format_args(args):
        return ''

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
