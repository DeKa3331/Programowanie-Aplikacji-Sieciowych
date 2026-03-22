#!/usr/bin/env python3

import socket
import sys
from datetime import datetime, timezone


HOST = "127.0.0.1"
PORT = 2916
MAX_LEN = 20


def now_str() -> str:
	return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def run_task_7_server(host: str, port: int) -> None:
	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

	try:
		server.bind((host, port))
	except OSError as error:
		print(f"Bind failed: {error}")
		sys.exit(1)

	server.listen(1)
	print(f"[{now_str()}] TCP fixed-length server is waiting for incoming connections on {host}:{port}...")

	try:
		while True:
			connection, address = server.accept()
			with connection:
				data = connection.recv(MAX_LEN)
				decoded = data.decode("utf-8", errors="replace")
				print(f"[{now_str()}] Received {len(data)} bytes from {address}. Data: {decoded}")

				if not data:
					continue

				normalized = data[:MAX_LEN].ljust(MAX_LEN, b" ")
				sent = connection.send(normalized)
				print(
					f"[{now_str()}] Sent {sent} bytes back to {address}. Data: {normalized.decode('utf-8', errors='replace')}"
				)
	finally:
		server.close()


def main() -> None:
	run_task_7_server(HOST, PORT)


if __name__ == "__main__":
	main()
