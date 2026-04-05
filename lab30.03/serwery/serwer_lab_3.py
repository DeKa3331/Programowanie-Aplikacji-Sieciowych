#!/usr/bin/env python3

import socket
import sys
import threading
from datetime import datetime, timezone


HOST = "127.0.0.1"
TCP_PORT = 5000
KNOCK_PORTS = (3666, 4666, 5666)
KNOCK_MESSAGE = "PING"
HIDDEN_MESSAGE = "Congratulations! You found the hidden."
BUFFER_SIZE = 1024


def now_str() -> str:
	return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def run_hidden_tcp_server(host: str, port: int, unlocked_event: threading.Event) -> None:
	print(f"[{now_str()}] TCP hidden service waiting to be unlocked on {host}:{port}...")
	unlocked_event.wait()

	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

	try:
		server.bind((host, port))
	except OSError as error:
		print(f"Bind failed for TCP service: {error}")
		return

	server.listen(1)
	print(f"[{now_str()}] TCP hidden service is now open on {host}:{port}.")

	try:
		while True:
			connection, address = server.accept()
			with connection:
				data = connection.recv(BUFFER_SIZE)
				decoded = data.decode("utf-8", errors="replace").strip()
				print(f"[{now_str()}] TCP client {address} sent: {decoded}")

				connection.sendall(HIDDEN_MESSAGE.encode("utf-8"))
				print(f"[{now_str()}] TCP response sent to {address}: {HIDDEN_MESSAGE}")
	finally:
		server.close()


def run_udp_knock_server(host: str, port: int, knock_state: dict[str, int], state_lock: threading.Lock, unlocked_event: threading.Event) -> None:
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

	try:
		sock.bind((host, port))
	except OSError as error:
		print(f"Bind failed for UDP port {port}: {error}")
		return

	print(f"[{now_str()}] UDP knock listener active on {host}:{port}.")

	try:
		while True:
			data, address = sock.recvfrom(BUFFER_SIZE)
			message = data.decode("utf-8", errors="replace").strip()
			print(f"[{now_str()}] UDP received on {port} from {address}: {message}")

			if message != KNOCK_MESSAGE:
				continue

			with state_lock:
				expected_port = KNOCK_PORTS[knock_state["index"]]

				if port == expected_port:
					knock_state["index"] += 1
					sock.sendto(b"PONG", address)
					print(f"[{now_str()}] UDP response sent to {address}: PONG")
					print(
						f"[{now_str()}] Knock progress: {knock_state['index']}/{len(KNOCK_PORTS)}"
					)

					if knock_state["index"] == len(KNOCK_PORTS):
						print(f"[{now_str()}] Correct knock sequence found. Opening TCP service.")
						unlocked_event.set()
				else:
					knock_state["index"] = 0
					print(f"[{now_str()}] Wrong knock order. Sequence reset.")
	finally:
		sock.close()


def main() -> None:
	print(f"[{now_str()}] Starting local port-knocking test server.")
	print(f"[{now_str()}] Hidden TCP service: {HOST}:{TCP_PORT}")
	print(f"[{now_str()}] UDP knock ports: {', '.join(str(port) for port in KNOCK_PORTS)}")
	print(f"[{now_str()}] Send '{KNOCK_MESSAGE}' to each UDP port in order.")

	unlocked_event = threading.Event()
	state_lock = threading.Lock()
	knock_state = {"index": 0}

	tcp_thread = threading.Thread(
		target=run_hidden_tcp_server,
		args=(HOST, TCP_PORT, unlocked_event),
		daemon=True,
	)
	tcp_thread.start()

	udp_threads = []
	for port in KNOCK_PORTS:
		thread = threading.Thread(
			target=run_udp_knock_server,
			args=(HOST, port, knock_state, state_lock, unlocked_event),
			daemon=True,
		)
		thread.start()
		udp_threads.append(thread)

	try:
		for thread in udp_threads:
			thread.join()
	except KeyboardInterrupt:
		print(f"[{now_str()}] Server interrupted by user.")


if __name__ == "__main__":
	main()
