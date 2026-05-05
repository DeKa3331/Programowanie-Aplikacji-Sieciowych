from __future__ import annotations

import socket
from urllib.parse import parse_qs


HOST = "127.0.0.1"
PORT = 8004
FORM_PATH = "/post"

FORM_PAGE = """<!DOCTYPE html>
<html lang="pl">
<head>
  <meta charset="utf-8">
  <title>Lab 9 - POST form</title>
</head>
<body>
  <h1>Formularz testowy</h1>
  <form method="post" action="/post">
    <label>Imie: <input name="name"></label><br>
    <label>Email: <input name="email" type="email"></label><br>
    <label>Wiadomosc:<br><textarea name="message" rows="5" cols="40"></textarea></label><br>
    <button type="submit">Wyslij</button>
  </form>
</body>
</html>
"""


def _read_request(connection: socket.socket) -> tuple[str, dict[str, str], bytes]:
	buffer = bytearray()
	separator = b"\r\n\r\n"
	while separator not in buffer:
		chunk = connection.recv(4096)
		if not chunk:
			break
		buffer.extend(chunk)

	headers_end = buffer.find(separator)
	if headers_end == -1:
		return buffer.decode("iso-8859-1", errors="replace"), {}, b""

	headers_raw = bytes(buffer[:headers_end]).decode("iso-8859-1", errors="replace")
	body = bytes(buffer[headers_end + len(separator):])

	headers: dict[str, str] = {}
	for line in headers_raw.split("\r\n")[1:]:
		if ":" in line:
			name, value = line.split(":", 1)
			headers[name.strip().lower()] = value.strip()

	content_length = int(headers.get("content-length", "0") or "0")
	while len(body) < content_length:
		chunk = connection.recv(4096)
		if not chunk:
			break
		body += chunk

	request_line = headers_raw.split("\r\n", 1)[0]
	return request_line, headers, body[:content_length]


def _build_response(status_line: str, headers: dict[str, str], body: bytes = b"") -> bytes:
	lines = [status_line]
	for name, value in headers.items():
		lines.append(f"{name}: {value}")
	lines.append("")
	return "\r\n".join(lines).encode("iso-8859-1") + b"\r\n" + body


def _html_escape(value: str) -> str:
	return (
		value.replace("&", "&amp;")
		.replace("<", "&lt;")
		.replace(">", "&gt;")
		.replace('"', "&quot;")
	)


def _handle_client(connection: socket.socket, address: tuple[str, int]) -> None:
	request_line, headers, body = _read_request(connection)
	print(f"[serwer_lab4] Client connected: {address[0]}:{address[1]}")
	print(f"[serwer_lab4] C: {request_line}")

	parts = request_line.split()
	method = parts[0] if len(parts) >= 1 else ""
	path = parts[1] if len(parts) >= 2 else ""

	if method == "GET" and path == FORM_PATH:
		response_body = FORM_PAGE.encode("utf-8")
		response = _build_response(
			"HTTP/1.1 200 OK",
			{
				"Content-Type": "text/html; charset=utf-8",
				"Content-Length": str(len(response_body)),
				"Connection": "close",
			},
			response_body,
		)
		connection.sendall(response)
		print("[serwer_lab4] Session finished (form page)")
		return

	if method == "POST" and path == FORM_PATH:
		form_data = parse_qs(body.decode("utf-8", errors="replace"), keep_blank_values=True)
		name = _html_escape(form_data.get("name", [""])[0])
		email = _html_escape(form_data.get("email", [""])[0])
		message = _html_escape(form_data.get("message", [""])[0])

		response_html = f"""<!DOCTYPE html>
<html lang="pl">
<head>
  <meta charset="utf-8">
  <title>Lab 9 - wynik POST</title>
</head>
<body>
  <h1>Odebrano formularz</h1>
  <p><strong>Imie:</strong> {name}</p>
  <p><strong>Email:</strong> {email}</p>
  <p><strong>Wiadomosc:</strong> {message}</p>
</body>
</html>
"""

		response_body = response_html.encode("utf-8")
		response = _build_response(
			"HTTP/1.1 200 OK",
			{
				"Content-Type": "text/html; charset=utf-8",
				"Content-Length": str(len(response_body)),
				"Connection": "close",
			},
			response_body,
		)
		connection.sendall(response)
		print(f"[serwer_lab4] Received form body: {body.decode('utf-8', errors='replace')}")
		print("[serwer_lab4] Session finished (form submission)")
		return

	body = b"Not Found"
	response = _build_response(
		"HTTP/1.1 404 Not Found",
		{
			"Content-Type": "text/plain; charset=utf-8",
			"Content-Length": str(len(body)),
			"Connection": "close",
		},
		body,
	)
	connection.sendall(response)


def main() -> None:
	print(f"[serwer_lab4] HTTP server listening on {HOST}:{PORT}")
	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
		server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		server_socket.bind((HOST, PORT))
		server_socket.listen(5)

		while True:
			connection, address = server_socket.accept()
			with connection:
				try:
					_handle_client(connection, address)
				except OSError as error:
					print(f"[serwer_lab4] Socket error: {error}")


if __name__ == "__main__":
	main()