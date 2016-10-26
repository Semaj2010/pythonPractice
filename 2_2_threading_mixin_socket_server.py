#!/usr/bin/env python
# -*- Coding: UTF-8 -*-
# Python Network Programming Cookbook -- Chapter -2
# This program is optimized for python 2.7
# It may run on any other version with/without modifications.

import os
import socket
import threading
import SocketServer

SERVER_HOST = 'localhost'
SERVER_PORT = 0 # tells the kernel to pickup a port dynamically
BUF_SIZE = 1024
ECHO_MSG = 'Hello echo Server!'

def client(ip, port, message):
    """ A client to test threading mixin server"""
    # Connect to the server
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))
    try:
        sock.sendall(message)
        response = sock.recv(BUF_SIZE)
        print "Clinet received: %s" %response
    finally:
        sock.close()

class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):
    """ An example of threaded TCP request handler """
    def handle(self):
        # Send the echo back to the client
        data = self.request.recv(BUF_SIZE)
        cur_thread = threading.current_thread()
        response = '%s: %s' % (cur_thread.name, data)
        print "Server sending response [current_process_id: data] = [%s]" %response
        self.request.send(response)
        return
class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    """ Nothing to add here, inherited everything necessary from parents"""
    pass

def main():
    # Run server
    server = ThreadedTCPServer((SERVER_HOST, SERVER_PORT), ThreadedTCPRequestHandler)
    ip, port = server.server_address # Retrieve the port number
    server_thread = threading.Thread(target=server.serve_forever)
    # Exit the server thread when the main thread exits
    server_thread.setDaemon(True) # Don't hang on exit
    server_thread.start()
    print 'Server loop running on thread: %s' % server_thread.name

    # Run clients
    client(ip, port, "Hello from client 1")
    client(ip, port, "Hello from client 2")
    client(ip, port, "Hello from client 3")

    #Clean them up
    server.shutdown()

if __name__ == '__main__':
    main()
