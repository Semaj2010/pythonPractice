#!/usr/bin/env python
# -*- Coding: UTF-8 -*-
# Python Network Programming Cookbook -- Chapter -1
# This program is optimized for python 3.4
# It may run on any other version with/without modifications.

import sys
import socket
import argparse

def main():
    # setup argument parsing
    parser = argparse.ArgumentParser(description='Socket Error Examples')
    parser.add_argument('--host', action="store", dest="host", required=False)
    parser.add_argument('--port', action='store', dest="port", type=int, required=False)
    parser.add_argument('--file', action="store", dest="file", required=False)
    given_args = parser.parse_args()
    host = given_args.host
    port = given_args.port
    filename = given_args.file

    # First try-except block -- create socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error as e:
        print("Error creating socket: %s" %e)
        sys.exit(1)

    # Second try-except block -- connect to given host/port
    try:
        s.connect((host,port))
    except socket.error as e:
        print("Connection error: %s" % e)
        sys.exit(1)

    # Third try-except block -- sending data
    try:
        s.sendall("Get %s HTTP/1.0\r\n\r\n" %filename)
    except socket.error as e:
        print("Error sending data: %s" % e)
        sys.exit(1)

    while 1:
        # Fourth tr-except block -- waiting to receive data from remote host
        try:
            buf = s.recv(2048)
        except socket.error as e:
            print("Error receiving data: %s" % e)
            sys.exit(1)
        if not len(buf):
            break
        # write the received data
        sys.stdout.write(buf)

if __name__ == '__main__':
    main()
