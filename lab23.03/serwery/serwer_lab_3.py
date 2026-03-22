#!/usr/bin/env python3

import socket
import sys
from datetime import datetime, timezone


HOST = "127.0.0.1"
PORT = 2912


def now_str() -> str:
	return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def run_task_3_server(host: str, port: int) -> None:
	server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

	try:
		server.bind((host, port))
	except OSError as error:
		print(f"Bind failed: {error}")
		sys.exit(1)

	print(f"[{now_str()}] UDP echo server is waiting for incoming datagrams on {host}:{port}...")

	try:
		while True:
			data, address = server.recvfrom(4096)
			decoded = data.decode("utf-8", errors="replace")
			print(
				f"[{now_str()}] Received {len(data)} bytes from {address}. Data: {decoded}"
			)

			if not data:
				continue

			sent = server.sendto(data, address)
			print(f"[{now_str()}] Sent {sent} bytes back to {address}. Data: {decoded}")
	finally:
		server.close()


def main() -> None:
	run_task_3_server(HOST, PORT)


if __name__ == "__main__":
	main()
