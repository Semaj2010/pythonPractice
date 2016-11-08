# -*- Coding: UTF-8 -*-

# socket, select module import
from socket import socket
from select import select
import sys
from time import ctime

# host, port, buffer size assign
HOST = ''
PORT = 56789
BUFSIZE = 1024
ADDR = (HOST, PORT)

# create socket object
servSock = socket(socket.AF_INET, socket.SOCK_STREAM)


# binding
servSock.bind(ADDR)

# listen
servSock.listen(10)
connection_list = [servSock]
print('===============================================')
print('채팅 서버를 시작합니다. %s 포트로 접속 대기' % str(PORT))
print('===============================================')

# start infinite loop
while connection_list:
    try:
        print('[INFO] 요청을 기다립니다...')

        # select 로 요청 받고, 10초마다 블럭킹 해제
        read_socket, write_socket, error_socket = select(connection_list, [], [], 10)

        for sock in read_socket:
            # new connect
            if sock == servSock:
                clntSock, addr_info = servSock.accept()
                connection_list.append(clntSock)
                print('[INFO][%s] 클라이언트(%s)가 새롭게 연결되었습니다.' % (ctime(), addr_info[0]))

                for socket_in_list in connection_list:
                    if socket_in_list != servSock and socket_in_list != sock:
                        try:
                            socket_in_list.send('[%s] 새로운 방문자가 대화방에 들어왔습니다.' % ctime())
                        except Exception as e:
                            socket_in_list.close()
                            connection_list.remove(socket_in_list)
                # 접속한 사용자로부터 새로운 데이터 받음
            else:
                data = sock.recv(BUFSIZE)
                if data:
                    print('[INFO][%s] 클라이언트로부터 데이터를 전달받았습니다,' % ctime())
                    for socket_in_list in connection_list:
                        if socket_in_list != servSock and socket_in_list != sock:
                            try:
                                socket_in_list.send('[%s] %s' % (ctime(), data))
                                print('[INFO][%s] 클라이언트로 데이터를 전달합니다' % ctime())
                            except Exception as e:
                                print(e.message)
                                socket_in_list.close()
                                connection_list.remove(socket_in_list)
                                continue
                        else:
                            connection_list.remove(sock)
                            sock.close()
                            print('[INFO][%s] 사용자와의 연결이 끊어졌습니다.' % ctime())
    except KeyboardInterrupt:
        servSock.close()
        sys.exit()

