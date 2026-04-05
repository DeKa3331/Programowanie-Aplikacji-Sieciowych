#!/usr/bin/env python3

import socket
import sys
import threading
from datetime import datetime, timezone


HOST = "127.0.0.1"
PORT = 5000
BUFFER_SIZE = 1024


def now_str() -> str:
	return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def run_tcp_server(host: str, port: int) -> None:
	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

	try:
		server.bind((host, port))
	except OSError as error:
		print(f"[{now_str()}] TCP bind failed: {error}")
		return

	server.listen(1)
	print(f"[{now_str()}] TCP echo server listening on {host}:{port}")

	try:
		while True:
			connection, address = server.accept()
			with connection:
				while True:
					data = connection.recv(BUFFER_SIZE)
					if not data:
						break

					connection.sendall(data)
					print(
						f"[{now_str()}] TCP {address}: received {len(data)} bytes and echoed them"
					)
	finally:
		server.close()


def run_udp_server(host: str, port: int) -> None:
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

	try:
		sock.bind((host, port))
	except OSError as error:
		print(f"[{now_str()}] UDP bind failed: {error}")
		return

	print(f"[{now_str()}] UDP echo server listening on {host}:{port}")

	try:
		while True:
			data, address = sock.recvfrom(BUFFER_SIZE)
			if not data:
				continue

			sock.sendto(data, address)
			print(
				f"[{now_str()}] UDP {address}: received {len(data)} bytes and echoed them"
			)
	finally:
		sock.close()


def main() -> None:
	print(f"[{now_str()}] Starting local TCP/UDP benchmark server on {HOST}:{PORT}")

	tcp_thread = threading.Thread(target=run_tcp_server, args=(HOST, PORT), daemon=True)
	udp_thread = threading.Thread(target=run_udp_server, args=(HOST, PORT), daemon=True)

	tcp_thread.start()
	udp_thread.start()

	try:
		tcp_thread.join()
		udp_thread.join()
	except KeyboardInterrupt:
		print(f"[{now_str()}] Server interrupted by user.")


if __name__ == "__main__":
	main()
