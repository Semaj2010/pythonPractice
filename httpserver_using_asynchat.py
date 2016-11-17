# http server using asynchat
import asynchat, asyncore, socket
import os
import mimetypes
try:
    from http.client import responses
except ImportError as e:
    from httplib import reponses

class async_http(asyncore.dispatcher):
    def __init__(self,port):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET,socket.SOCK_STREAM)
        self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
        self.bind(('',port))
        self.listen(5)

    def handle_accept(self):
        client, addr = self.accept()
        return async_http_handler(client)

# handle async http request
class async_http_handler(asynchat.async_chat):
    def __init__(self,conn=None):
        asynchat.async_chat.__init__(self,conn)
        self.data = []
        self.got_header = Falser
        self.set_terminator(b"\r\n\r\n")

    def collect_incoming_data(self,data):
        if not self.got_header:
            self.data.append(data)

    # blank line = exit
    def found_terminator(self):
        self.got_header = True
        header_data = b"".join(self.data)
        # decode header data to text
        header_text = header_data.decode('latin-1')
        header_lines = header_text.splitlines()
        request = header_lines[0].split()
        op = request[0]
        url = request[1][1:]
        self.process_request(op,url)

    # put text to outputstream, after encoding
    def push_text(self,text):
        self.push(text.encode('latin-1'))

    # handle request
    def process_request(self,op, url):
        if op == "GET":
            if not os.path.exists(url):
                self.send_error(404,"File %s not found\r\n" % url)
            else:
                type, encoding = mimetypes.guess_type(url)
                size = os.path.getsize(url)
                self.push_text("HTTP/1.0 200 OK\r\n")
                self.push_text("Content-length: %s\r\n" % size)
                self.push_text("Content-type: %s\r\n" % type)
                self.push_text("\r\n")
                self.push_with_producer(file_producer(url))
        else:
            self.send_error(501,"%s method not implemented" % op)
        self.close_when_done()
    # handle error
    def send_error(self, code, message):
        self.push_text("HTTP/1.0 %s %s\r\n" % (code, responses[code]))
        self.push_text("Content-type L text/plain\r\n")
        self.push_text("\r\n")
        self.push_text(message)

class file_producer(object):
    def __init__(self,filename, buffer_size=512):
        self.f = open(filename,"rb")
        self.buffer_size = buffer_size
    def more(self):
        data = self.f.read(self.buffer_size)
        if not data:
            self.f.close()
        return data

a = async_http(8080)
asyncore.loop()

