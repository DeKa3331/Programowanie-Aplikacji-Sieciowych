# !/usr/bin/env python

import socket
import sys
from time import gmtime, strftime

HOST = '127.0.0.1'
PORT = 2907

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

try:
    sock.bind((HOST, PORT))
except socket.error as msg:
    print('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + str(msg[1]))
    sys.exit()

print("[%s] UDP ECHO Server is waiting for incoming connections on port %s ... " % (strftime("%Y-%m-%d %H:%M:%S", gmtime()), PORT))

try:
    while True:
        try:
            data, address = sock.recvfrom(4096)
        except OSError as error:
            if getattr(error, "winerror", None) == 10054:
                print('[%s] Ignoring WinError 10054 (client closed/reset UDP endpoint).' % (strftime("%Y-%m-%d %H:%M:%S", gmtime())))
                continue
            raise

        print('[%s] Received %s bytes from client %s. Data: %s' % (strftime("%Y-%m-%d %H:%M:%S", gmtime()), len(data), address, data))

        if data:

            try:

                hostname_text = data.decode("ascii", errors="strict").strip()
                ip_address = socket.gethostbyname(hostname_text)
                sent = sock.sendto(ip_address.encode("utf-8"), address)
                print('[%s] Sent %s bytes bytes back to client %s.' % (strftime("%Y-%m-%d %H:%M:%S", gmtime()), sent, address))

            except (socket.gaierror, UnicodeDecodeError):
                sent = sock.sendto("Sorry, an error occurred in gethostbyname".encode("utf-8"), address)
                print('[%s] Sent %s bytes bytes back to client %s.' % (strftime("%Y-%m-%d %H:%M:%S", gmtime()), sent, address))
finally:
    sock.close()