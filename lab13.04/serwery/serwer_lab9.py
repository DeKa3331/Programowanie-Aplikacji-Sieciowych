import socket


HOST = "127.0.0.1"
PORT = 2533
BUFFER_SIZE = 4096


def send_line(connection: socket.socket, text: str) -> None:
	connection.sendall((text + "\r\n").encode("utf-8"))


def run_server() -> None:
	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
		server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		server_socket.bind((HOST, PORT))
		server_socket.listen(1)

		print(f"[serwer_lab9] SMTP HTML server on {HOST}:{PORT}")
		print("[serwer_lab9] Waiting for one client...")

		connection, address = server_socket.accept()
		with connection:
			print(f"[serwer_lab9] Client connected: {address}")
			connection.settimeout(120)

			send_line(connection, "220 localhost SMTP test server ready")

			buffer = b""
			data_mode = False
			message_lines: list[str] = []

			while True:
				chunk = connection.recv(BUFFER_SIZE)
				if not chunk:
					print("[serwer_lab9] Client disconnected")
					break

				buffer += chunk

				while b"\n" in buffer:
					raw_line, buffer = buffer.split(b"\n", 1)
					line = raw_line.decode("utf-8", errors="replace").rstrip("\r")
					print(f"[serwer_lab9] C: {line}")

					if data_mode:
						if line == ".":
							joined = "\n".join(message_lines).lower()
							has_html = "content-type: text/html" in joined
							has_bold = "<b>" in joined or "<i>" in joined or "<u>" in joined

							print(f"[serwer_lab9] HTML content-type present: {has_html}")
							print(f"[serwer_lab9] HTML formatting tags present: {has_bold}")

							if has_html and has_bold:
								send_line(connection, "250 HTML message accepted")
							else:
								send_line(connection, "550 HTML headers missing for zad9")

							message_lines.clear()
							data_mode = False
						else:
							message_lines.append(line)
						continue

					upper_line = line.upper()

					if upper_line.startswith("EHLO") or upper_line.startswith("HELO"):
						send_line(connection, "250-localhost")
						send_line(connection, "250 SIZE 10485760")
					elif upper_line.startswith("MAIL FROM:"):
						send_line(connection, "250 OK")
					elif upper_line.startswith("RCPT TO:"):
						send_line(connection, "250 OK")
					elif upper_line == "DATA":
						data_mode = True
						send_line(connection, "354 End data with <CR><LF>.<CR><LF>")
					elif upper_line == "QUIT":
						send_line(connection, "221 Bye")
						print("[serwer_lab9] Session finished")
						return
					else:
						send_line(connection, "500 Command unrecognized")


def main() -> None:
	try:
		run_server()
	except OSError as error:
		print(f"[serwer_lab9] Socket error: {error}")


if __name__ == "__main__":
	main()
