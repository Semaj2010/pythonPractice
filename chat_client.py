# -*- Coding: UTF-8 -*-
# socket module import
import socket
from select import select
import sys


# HOST, PORT, BUFFER SIZE
HOST = '127.0.0.1'
PORT = 56789
BUFSIZE = 1024
ADDR = (HOST, PORT)

# Socket object create
clntSock = socket(socket.AF_INET, socket.SOCK_STREAM)

# try to connect to server
try:
    clntSock.connect(ADDR)
except Exception as e:
    print('채팅 서버(%s:%s)에 연결 할 수 없습니다.' % ADDR)
    sys.exit()
print('채팅 서버(%s:%s)에 연결 되었습니다.' % ADDR)


def prompt():
    sys.stdout.write('<나> ')
    sys.stdout.flush()

# 무한 루프 시작
while True:
    try:
        connection_list = [sys.stdin, clntSock]

        read_socket, wrtie_socket, error_socket = select(connection_list, [], [], 10)

        for sock in read_socket:
            if sock == clntSock:
                data = sock.recv(BUFSIZE)
                if not data:
                    print('채팅 서버(%s:%s)와의 연결이 끊어졌습니다.' % ADDR)
                    clntSock.close()
                    sys.exit()
                else:
                    print('%s' % data)
                    prompt()
            else:
                message = sys.stdin.readline()
                clntSock.send(message)
                prompt()
    except KeyboardInterrupt:
        clntSock.close()
        sys.exit()
