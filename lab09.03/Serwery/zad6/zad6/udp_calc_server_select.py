#!/usr/bin/env python

#tutaj musialem troche poprawic w serwerze, bo nowszy python 
import socket
import sys
from time import gmtime, strftime

HOST = '127.0.0.1'
PORT = 2902

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

try:
    sock.bind((HOST, PORT))
except socket.error as msg:
    print('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
    sys.exit()

print("[%s] UDP Calc Server is waiting for incoming connections ... " % strftime("%Y-%m-%d %H:%M:%S", gmtime()))

try:
    while True:

        data1, address = sock.recvfrom(4096)
        op, address = sock.recvfrom(4096)
        data2, address = sock.recvfrom(4096)

        if data1 and data2 and op:

            data1_text = data1.decode("utf-8", errors="replace").strip()
            op_text = op.decode("utf-8", errors="replace").strip()
            data2_text = data2.decode("utf-8", errors="replace").strip()

            print("[%s] Got from client %s ... : %s %s %s" % (strftime("%Y-%m-%d %H:%M:%S", gmtime()), str(address), data1_text, op_text, data2_text))

            try :

                if op_text == '+':
                    result = float(data1_text) + float(data2_text)
                    sent = sock.sendto(str(result).encode("utf-8"), address)
                elif op_text == '-':
                    result = float(data1_text) - float(data2_text)
                    sent = sock.sendto(str(result).encode("utf-8"), address)
                elif op_text == '*':
                    result = float(data1_text) * float(data2_text)
                    sent = sock.sendto(str(result).encode("utf-8"), address)
                elif op_text == '/':
                    result = float(data1_text) / float(data2_text)
                    sent = sock.sendto(str(result).encode("utf-8"), address)
                else:
                    result = "Bad operator. I support only +, -, *, / math operators"
                    sent = sock.sendto(str(result).encode("utf-8"), address)

            except ValueError as e:
                result = "%s" % e
                sent = sock.sendto(str(result).encode("utf-8"), address)

            except:
                result = "Error"
                sent = sock.sendto(str(result).encode("utf-8"), address)
finally:

    sock.close()
