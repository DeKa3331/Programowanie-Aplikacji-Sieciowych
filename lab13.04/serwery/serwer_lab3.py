import socket


HOST = "127.0.0.1"
PORT = 2527
BUFFER_SIZE = 4096


def send_line(connection: socket.socket, text: str) -> None:
	connection.sendall((text + "\r\n").encode("utf-8"))


def run_server() -> None:
	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
		server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		server_socket.bind((HOST, PORT))
		server_socket.listen(1)

		print(f"[serwer_lab3] SMTP spoof-demo server on {HOST}:{PORT}")
		print("[serwer_lab3] Waiting for one client...")

		connection, address = server_socket.accept()
		with connection:
			print(f"[serwer_lab3] Client connected: {address}")
			connection.settimeout(120)

			send_line(connection, "220 localhost SMTP test server ready")

			buffer = b""
			data_mode = False
			message_lines: list[str] = []
			envelope_from = ""

			while True:
				chunk = connection.recv(BUFFER_SIZE)
				if not chunk:
					print("[serwer_lab3] Client disconnected")
					break

				buffer += chunk

				while b"\n" in buffer:
					raw_line, buffer = buffer.split(b"\n", 1)
					line = raw_line.decode("utf-8", errors="replace").rstrip("\r")
					print(f"[serwer_lab3] C: {line}")

					if data_mode:
						if line == ".":
							header_from = ""
							for msg_line in message_lines:
								if msg_line.lower().startswith("from:"):
									header_from = msg_line.split(":", 1)[1].strip()
									break

							print(f"[serwer_lab3] Envelope MAIL FROM: {envelope_from}")
							print(f"[serwer_lab3] Header From: {header_from}")
							if header_from and envelope_from and header_from.strip("<>") != envelope_from.strip("<>"):
								print("[serwer_lab3] SPOOF DETECTED: envelope and header From are different")
							else:
								print("[serwer_lab3] No spoof mismatch detected")

							message_lines.clear()
							data_mode = False
							send_line(connection, "250 Message accepted for delivery")
						else:
							message_lines.append(line)
						continue

					upper_line = line.upper()

					if upper_line.startswith("EHLO") or upper_line.startswith("HELO"):
						send_line(connection, "250-localhost")
						send_line(connection, "250 SIZE 10485760")
					elif upper_line.startswith("MAIL FROM:"):
						envelope_from = line.split(":", 1)[1].strip()
						send_line(connection, "250 OK")
					elif upper_line.startswith("RCPT TO:"):
						send_line(connection, "250 OK")
					elif upper_line == "DATA":
						data_mode = True
						send_line(connection, "354 End data with <CR><LF>.<CR><LF>")
					elif upper_line == "QUIT":
						send_line(connection, "221 Bye")
						print("[serwer_lab3] Session finished")
						return
					else:
						send_line(connection, "500 Command unrecognized")


def main() -> None:
	try:
		run_server()
	except OSError as error:
		print(f"[serwer_lab3] Socket error: {error}")


if __name__ == "__main__":
	main()
