#!/usr/bin/env python3

import socket
import sys
from datetime import datetime, timezone


HOST = "127.0.0.1"
PORT = 2917
EXACT_LEN = 20


def now_str() -> str:
	return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def recv_exact(connection: socket.socket, expected_len: int) -> bytes:
	chunks: list[bytes] = []
	received_len = 0

	while received_len < expected_len:
		part = connection.recv(expected_len - received_len)
		if not part:
			raise OSError("Połączenie zostało zamknięte podczas odbierania danych.")
		chunks.append(part)
		received_len += len(part)

	return b"".join(chunks)


def send_exact(connection: socket.socket, data: bytes) -> None:
	total_sent = 0

	while total_sent < len(data):
		sent = connection.send(data[total_sent:])
		if sent == 0:
			raise OSError("Połączenie zostało zamknięte podczas wysyłania danych.")
		total_sent += sent


def run_task_8_server(host: str, port: int) -> None:
	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

	try:
		server.bind((host, port))
	except OSError as error:
		print(f"Bind failed: {error}")
		sys.exit(1)

	server.listen(1)
	print(f"[{now_str()}] TCP exact-length server is waiting for incoming connections on {host}:{port}...")

	try:
		while True:
			connection, address = server.accept()
			with connection:
				try:
					data = recv_exact(connection, EXACT_LEN)
				except OSError as error:
					print(f"[{now_str()}] Receive error from {address}: {error}")
					continue

				decoded = data.decode("utf-8", errors="replace")
				print(f"[{now_str()}] Received exactly {len(data)} bytes from {address}. Data: {decoded}")

				try:
					send_exact(connection, data)
				except OSError as error:
					print(f"[{now_str()}] Send error to {address}: {error}")
					continue

				print(f"[{now_str()}] Sent exactly {len(data)} bytes back to {address}.")
	finally:
		server.close()


def main() -> None:
	run_task_8_server(HOST, PORT)


if __name__ == "__main__":
	main()
