#!/usr/bin/env python3

import random
import socket
import sys
from datetime import datetime, timezone


HOST = "127.0.0.1"
PORT = 5000
BUFFER_SIZE = 1024
RANGE_START = 1
RANGE_END = 100


def now_str() -> str:
	return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def run_task_2_server(host: str, port: int) -> None:
	secret = random.randint(RANGE_START, RANGE_END)
	print(f"[{now_str()}] Guess server picked number from {RANGE_START}..{RANGE_END}.")

	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

	try:
		server.bind((host, port))
	except OSError as error:
		print(f"Bind failed: {error}")
		sys.exit(1)

	server.listen(1)
	print(f"[{now_str()}] TCP guess server is waiting for incoming connections on {host}:{port}...")

	try:
		while True:
			connection, address = server.accept()
			with connection:
				print(f"[{now_str()}] Client connected: {address}")

				while True:
					data = connection.recv(BUFFER_SIZE)
					decoded = data.decode("utf-8", errors="replace").strip()
					print(
						f"[{now_str()}] Received {len(data)} bytes from {address}. Data: {decoded}"
					)

					if not data:
						print(f"[{now_str()}] Client closed connection: {address}")
						break

					try:
						guess = int(decoded)
					except ValueError:
						response = "BLAD: przeslij liczbe calkowita."
						connection.sendall(response.encode("utf-8"))
						print(f"[{now_str()}] Sent to {address}: {response}")
						continue

					if guess < secret:
						response = "Za mala liczba."
						connection.sendall(response.encode("utf-8"))
						print(f"[{now_str()}] Sent to {address}: {response}")
					elif guess > secret:
						response = "Za duza liczba."
						connection.sendall(response.encode("utf-8"))
						print(f"[{now_str()}] Sent to {address}: {response}")
					else:
						response = "Brawo! Odgadles liczbe."
						connection.sendall(response.encode("utf-8"))
						print(f"[{now_str()}] Sent to {address}: {response}")
						print(f"[{now_str()}] Number guessed. Server is shutting down.")
						return
	finally:
		server.close()


def main() -> None:
	run_task_2_server(HOST, PORT)


if __name__ == "__main__":
	main()
