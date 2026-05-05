import gzip
import socket
import time
import zlib
from urllib.parse import urlencode
from pathlib import Path
from typing import Callable


TASK1_HOST = "127.0.0.1"
TASK1_PORT = 8001
TASK1_PATH = "/html"
TASK1_OUTPUT = "zad1.html"

TASK2_HOST = "127.0.0.1"
TASK2_PORT = 8002
TASK2_PATH = "/image/png"
TASK2_OUTPUT = "zad2.png"

TASK3_HOST = "127.0.0.1"
TASK3_PORT = 8003
TASK3_PATH = "/image.jpg"
TASK3_OUTPUT = "zad3.jpg"

TASK4_HOST = "127.0.0.1"
TASK4_PORT = 8004
TASK4_PATH = "/post"

TASK5_HOST = "127.0.0.1"
TASK5_PORT = 8005
TASK5_PATH = "/"
TASK5_CONNECTIONS = 20
TASK5_DELAY_SECONDS = 1.0
TASK5_ROUNDS = 5

TASK6_HOST = "127.0.0.1"
TASK6_PORT = 8006
TASK6_PATH = "/image.jpg"
TASK6_OUTPUT = "zad6.jpg"
TASK6_META = "zad6.last_modified.txt"

TASK7_HOST = "127.0.0.1"
TASK7_PORT = 8007
TASK7_PATH_OK = "/"
TASK7_PATH_404 = "/brak"

SAFARI_703_USER_AGENT = (
	"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) "
	"AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/7046A194A"
)

TASK_TOGGLES: dict[int, bool] = {
	1: True,
	2: True,
	3: True,
	4: True,
	5: True,
	6: True,
	7: True,
}


def _read_http_response(connection: socket.socket) -> tuple[int, str, dict[str, str], bytes]:
	buffer = bytearray()
	separator = b"\r\n\r\n"

	while separator not in buffer:
		chunk = connection.recv(4096)
		if not chunk:
			raise OSError("Server closed the connection before sending complete headers.")
		buffer.extend(chunk)

	headers_end = buffer.index(separator)
	headers_raw = bytes(buffer[:headers_end])
	body = bytes(buffer[headers_end + len(separator):])

	header_lines = headers_raw.decode("iso-8859-1", errors="replace").split("\r\n")
	if not header_lines:
		raise RuntimeError("Empty HTTP response.")

	status_line = header_lines[0]
	parts = status_line.split(" ", 2)
	if len(parts) < 2 or not parts[1].isdigit():
		raise RuntimeError(f"Invalid HTTP status line: {status_line}")

	status_code = int(parts[1])
	reason = parts[2] if len(parts) > 2 else ""

	headers: dict[str, str] = {}
	for line in header_lines[1:]:
		if ":" not in line:
			continue
		name, value = line.split(":", 1)
		headers[name.strip().lower()] = value.strip()

	content_length = headers.get("content-length")
	if content_length is not None:
		try:
			expected_length = int(content_length)
		except ValueError as error:
			raise RuntimeError(f"Invalid Content-Length header: {content_length}") from error

		while len(body) < expected_length:
			chunk = connection.recv(4096)
			if not chunk:
				break
			body += chunk

		body = body[:expected_length]
	else:
		while True:
			chunk = connection.recv(4096)
			if not chunk:
				break
			body += chunk

	return status_code, reason, headers, body


def _send_http_request(connection: socket.socket, request: str) -> None:
	connection.sendall(request.encode("utf-8"))


def _build_request(method: str, host: str, path: str, headers: dict[str, str]) -> str:
	lines = [f"{method} {path} HTTP/1.1", f"Host: {host}"]
	for name, value in headers.items():
		lines.append(f"{name}: {value}")
	lines.append("")
	lines.append("")
	return "\r\n".join(lines)


def _build_request_with_body(
	method: str,
	host: str,
	path: str,
	headers: dict[str, str],
	body: bytes,
) -> bytes:
	lines = [f"{method} {path} HTTP/1.1", f"Host: {host}"]
	for name, value in headers.items():
		lines.append(f"{name}: {value}")
	lines.append("")
	request_head = "\r\n".join(lines).encode("utf-8") + b"\r\n"
	return request_head + body


def _log_request_headers(log_prefix: str, headers: dict[str, str]) -> None:
	print(f"[{log_prefix}] Uzyte naglowki:")
	for name, value in headers.items():
		print(f"[{log_prefix}]   {name}: {value}")


def _save_bytes(output_name: str, payload: bytes) -> Path:
	output_path = Path(__file__).resolve().with_name(output_name)
	output_path.write_bytes(payload)
	return output_path


def _save_text(output_name: str, text: str) -> Path:
	output_path = Path(__file__).resolve().with_name(output_name)
	output_path.write_text(text, encoding="utf-8")
	return output_path


def _load_text_if_exists(output_name: str) -> str | None:
	output_path = Path(__file__).resolve().with_name(output_name)
	if not output_path.exists():
		return None
	return output_path.read_text(encoding="utf-8").strip() or None


def _decode_body(response_headers: dict[str, str], body: bytes) -> bytes:
	content_encoding = response_headers.get("content-encoding", "").lower()
	if content_encoding == "gzip":
		return gzip.decompress(body)

	if content_encoding == "deflate":
		try:
			return zlib.decompress(body)
		except zlib.error:
			return zlib.decompress(body, -zlib.MAX_WBITS)

	return body


def task_1() -> None:
	print(f"[zad1] HTTP GET /html -> {TASK1_HOST}:{TASK1_PORT}")

	headers = {
		"User-Agent": SAFARI_703_USER_AGENT,
		"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
		"Accept-Language": "en-us",
		"Accept-Encoding": "gzip, deflate",
		"Connection": "close",
	}

	_log_request_headers("zad1", headers)

	try:
		with socket.create_connection((TASK1_HOST, TASK1_PORT), timeout=15) as connection:
			connection.settimeout(15)
			request = _build_request("GET", TASK1_HOST, TASK1_PATH, headers)
			print(f"[zad1] C: GET {TASK1_PATH} HTTP/1.1")
			_send_http_request(connection, request)

			status_code, reason, response_headers, body = _read_http_response(connection)
			print(f"[zad1] S: HTTP/1.1 {status_code} {reason}")

			decoded_body = _decode_body(response_headers, body)
			output_path = _save_bytes(TASK1_OUTPUT, decoded_body)
			print(f"[zad1] Zapisano plik: {output_path}")
			content_type = response_headers.get("content-type", "brak")
			print(f"[zad1] Content-Type: {content_type}")
			print("[zad1] Zakonczono pomyslnie.")
	except (OSError, RuntimeError, TimeoutError) as error:
		print(f"[zad1] Error: {error}")


def task_2() -> None:
	print(f"[zad2] HTTP GET /image/png -> {TASK2_HOST}:{TASK2_PORT}")

	headers = {
		"User-Agent": SAFARI_703_USER_AGENT,
		"Accept": "image/png,image/*;q=0.8,*/*;q=0.5",
		"Accept-Language": "en-us",
		"Accept-Encoding": "gzip, deflate",
		"Connection": "close",
	}

	_log_request_headers("zad2", headers)

	try:
		with socket.create_connection((TASK2_HOST, TASK2_PORT), timeout=15) as connection:
			connection.settimeout(15)
			request = _build_request("GET", TASK2_HOST, TASK2_PATH, headers)
			print(f"[zad2] C: GET {TASK2_PATH} HTTP/1.1")
			_send_http_request(connection, request)

			status_code, reason, response_headers, body = _read_http_response(connection)
			print(f"[zad2] S: HTTP/1.1 {status_code} {reason}")

			decoded_body = _decode_body(response_headers, body)
			output_path = _save_bytes(TASK2_OUTPUT, decoded_body)
			print(f"[zad2] Zapisano plik: {output_path}")
			content_type = response_headers.get("content-type", "brak")
			print(f"[zad2] Content-Type: {content_type}")
			print("[zad2] Zakonczono pomyslnie.")
	except (OSError, RuntimeError, TimeoutError) as error:
		print(f"[zad2] Error: {error}")


def _parse_content_length(headers: dict[str, str]) -> int:
	content_length = headers.get("content-length")
	if content_length is None:
		raise RuntimeError("Brak naglowka Content-Length w odpowiedzi HEAD/GET.")

	try:
		return int(content_length)
	except ValueError as error:
		raise RuntimeError(f"Niepoprawny Content-Length: {content_length}") from error


def _parse_total_size_from_content_range(content_range: str) -> int:
	if "/" not in content_range:
		raise RuntimeError(f"Niepoprawny Content-Range: {content_range}")

	total_part = content_range.rsplit("/", 1)[1].strip()
	if total_part == "*":
		raise RuntimeError(f"Nieznany rozmiar pliku w Content-Range: {content_range}")

	try:
		return int(total_part)
	except ValueError as error:
		raise RuntimeError(f"Niepoprawny rozmiar pliku w Content-Range: {content_range}") from error


def _discover_remote_size(host: str, port: int, path: str, headers: dict[str, str]) -> int:
	with socket.create_connection((host, port), timeout=15) as connection:
		connection.settimeout(15)
		request = _build_request("HEAD", host, path, headers)
		print(f"[zad3] C: HEAD {path} HTTP/1.1")
		_send_http_request(connection, request)
		status_code, reason, response_headers, _ = _read_http_response(connection)
		print(f"[zad3] S: HTTP/1.1 {status_code} {reason}")

		if status_code in {200, 206} and response_headers.get("content-length") is not None:
			return _parse_content_length(response_headers)

	print("[zad3] HEAD nie wystarczyl, probuje GET z Range 0-0.")
	fallback_headers = dict(headers)
	fallback_headers["Range"] = "bytes=0-0"
	fallback_request = _build_request("GET", host, path, fallback_headers)
	with socket.create_connection((host, port), timeout=15) as connection:
		connection.settimeout(15)
		print(f"[zad3] C: GET {path} HTTP/1.1")
		print("[zad3]   Range: bytes=0-0")
		_send_http_request(connection, fallback_request)
		status_code, reason, response_headers, _ = _read_http_response(connection)
		print(f"[zad3] S: HTTP/1.1 {status_code} {reason}")

		content_range = response_headers.get("content-range")
		if content_range is None:
			raise RuntimeError("Nie udalo sie odczytac Content-Range w odpowiedzi fallback.")

		return _parse_total_size_from_content_range(content_range)


def _download_range(host: str, port: int, path: str, headers: dict[str, str], start: int, end: int, log_prefix: str) -> bytes:
	request_headers = dict(headers)
	request_headers["Range"] = f"bytes={start}-{end}"
	request_headers["Connection"] = "close"
	request = _build_request("GET", host, path, request_headers)

	print(f"[{log_prefix}] C: GET {path} HTTP/1.1")
	print(f"[{log_prefix}]   Range: bytes={start}-{end}")

	with socket.create_connection((host, port), timeout=15) as connection:
		connection.settimeout(15)
		_send_http_request(connection, request)
		status_code, reason, response_headers, body = _read_http_response(connection)
		print(f"[{log_prefix}] S: HTTP/1.1 {status_code} {reason}")

		if status_code not in {200, 206}:
			raise RuntimeError(f"Unexpected HTTP status {status_code} for range {start}-{end}.")

		content_range = response_headers.get("content-range")
		if content_range is not None:
			print(f"[{log_prefix}] Content-Range: {content_range}")

		return body


def task_3() -> None:
	print(f"[zad3] HTTP GET /image.jpg w 3 czesciach -> {TASK3_HOST}:{TASK3_PORT}")

	headers = {
		"User-Agent": SAFARI_703_USER_AGENT,
		"Accept": "image/jpeg,image/*;q=0.8,*/*;q=0.5",
		"Connection": "close",
	}

	_log_request_headers("zad3", headers)

	try:
		total_size = _discover_remote_size(TASK3_HOST, TASK3_PORT, TASK3_PATH, headers)
		if total_size <= 0:
			raise RuntimeError("Rozmiar pliku musi byc dodatni.")

		part_size = total_size // 3
		boundaries = [
			(0, part_size - 1),
			(part_size, part_size * 2 - 1),
			(part_size * 2, total_size - 1),
		]

		assembled = bytearray()
		for index, (start, end) in enumerate(boundaries, start=1):
			if start > end:
				continue
			print(f"[zad3] Pobieram czesc {index}: bytes {start}-{end}")
			chunk = _download_range(TASK3_HOST, TASK3_PORT, TASK3_PATH, headers, start, end, f"zad3/{index}")
			assembled.extend(chunk)

		if len(assembled) != total_size:
			print(f"[zad3] Uwaga: zlozony rozmiar {len(assembled)} nie zgadza sie z oczekiwanym {total_size}.")

		output_path = _save_bytes(TASK3_OUTPUT, bytes(assembled))
		print(f"[zad3] Zapisano plik: {output_path}")
		print("[zad3] Zakonczono pomyslnie.")
	except (OSError, RuntimeError, TimeoutError) as error:
		print(f"[zad3] Error: {error}")


def task_4() -> None:
	print(f"[zad4] HTTP POST /post -> {TASK4_HOST}:{TASK4_PORT}")

	name = input("[zad4] Imie: ").strip()
	email = input("[zad4] Email: ").strip()
	message = input("[zad4] Wiadomosc: ").strip()

	if not name or not email or not message:
		print("[zad4] Wszystkie pola sa wymagane.")
		return

	form_data = {
		"name": name,
		"email": email,
		"message": message,
	}
	body = urlencode(form_data).encode("utf-8")

	headers = {
		"User-Agent": SAFARI_703_USER_AGENT,
		"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
		"Accept-Language": "en-us",
		"Content-Type": "application/x-www-form-urlencoded",
		"Content-Length": str(len(body)),
		"Connection": "close",
	}

	_log_request_headers("zad4", headers)

	try:
		with socket.create_connection((TASK4_HOST, TASK4_PORT), timeout=15) as connection:
			connection.settimeout(15)
			request = _build_request_with_body("POST", TASK4_HOST, TASK4_PATH, headers, body)
			print(f"[zad4] C: POST {TASK4_PATH} HTTP/1.1")
			print(f"[zad4] C: {body.decode('utf-8', errors='replace')}")
			connection.sendall(request)

			status_code, reason, response_headers, response_body = _read_http_response(connection)
			print(f"[zad4] S: HTTP/1.1 {status_code} {reason}")

			decoded_body = _decode_body(response_headers, response_body)
			print(decoded_body.decode("utf-8", errors="replace"))
			print("[zad4] Zakonczono pomyslnie.")
	except (OSError, RuntimeError, TimeoutError) as error:
		print(f"[zad4] Error: {error}")


def task_5() -> None:
	print(f"[zad5] Slowloris demo -> {TASK5_HOST}:{TASK5_PORT}")

	headers = {
		"User-Agent": SAFARI_703_USER_AGENT,
		"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
		"Connection": "keep-alive",
	}

	_log_request_headers("zad5", headers)

	connections: list[socket.socket] = []
	try:
		for index in range(TASK5_CONNECTIONS):
			connection = socket.create_connection((TASK5_HOST, TASK5_PORT), timeout=15)
			connection.settimeout(15)
			connections.append(connection)
			request_head = [
				f"GET {TASK5_PATH} HTTP/1.1",
				f"Host: {TASK5_HOST}",
				f"User-Agent: {headers['User-Agent']}",
				"Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
				"Connection: keep-alive",
				"X-a: b",
				"",
			]
			payload = "\r\n".join(request_head).encode("utf-8")
			connection.sendall(payload)
			print(f"[zad5] Otworzono polaczenie #{index + 1}")

		for round_index in range(TASK5_ROUNDS):
			time.sleep(TASK5_DELAY_SECONDS)
			alive_connections = 0
			for index, connection in enumerate(list(connections), start=1):
				try:
					connection.sendall(b"X-a: b\r\n")
					alive_connections += 1
				except OSError:
					try:
						connection.close()
					except OSError:
						pass
					connections.remove(connection)
					try:
						replacement = socket.create_connection((TASK5_HOST, TASK5_PORT), timeout=15)
						replacement.settimeout(15)
						replacement.sendall(b"GET / HTTP/1.1\r\nHost: 127.0.0.1\r\nConnection: keep-alive\r\nX-a: b\r\n")
						connections.append(replacement)
					except OSError as error:
						print(f"[zad5] Nie udalo sie odtworzyc polaczenia #{index}: {error}")
			print(f"[zad5] Runda {round_index + 1}/{TASK5_ROUNDS}, aktywne polaczenia: {alive_connections}")

		print("[zad5] Slowloris demo zakonczone.")
	except (OSError, RuntimeError, TimeoutError) as error:
		print(f"[zad5] Error: {error}")
	finally:
		for connection in connections:
			try:
				connection.close()
			except OSError:
				pass


def task_6() -> None:
	print(f"[zad6] Conditional GET image -> {TASK6_HOST}:{TASK6_PORT}")

	headers = {
		"User-Agent": SAFARI_703_USER_AGENT,
		"Accept": "image/jpeg,image/*;q=0.8,*/*;q=0.5",
		"Connection": "close",
	}

	cached_last_modified = _load_text_if_exists(TASK6_META)
	if cached_last_modified:
		headers["If-Modified-Since"] = cached_last_modified
		print(f"[zad6] Uzywam If-Modified-Since: {cached_last_modified}")

	_log_request_headers("zad6", headers)

	try:
		with socket.create_connection((TASK6_HOST, TASK6_PORT), timeout=15) as connection:
			connection.settimeout(15)

			if cached_last_modified is None:
				request = _build_request("HEAD", TASK6_HOST, TASK6_PATH, headers)
				print(f"[zad6] C: HEAD {TASK6_PATH} HTTP/1.1")
			else:
				request = _build_request("HEAD", TASK6_HOST, TASK6_PATH, headers)
				print(f"[zad6] C: HEAD {TASK6_PATH} HTTP/1.1")

			_send_http_request(connection, request)
			status_code, reason, response_headers, _ = _read_http_response(connection)
			print(f"[zad6] S: HTTP/1.1 {status_code} {reason}")

			current_last_modified = response_headers.get("last-modified")
			if status_code == 304:
				print("[zad6] Obrazek nie zmienil sie od ostatniego pobrania.")
				return

			if current_last_modified is None:
				raise RuntimeError("Brak Last-Modified w odpowiedzi serwera.")

			if cached_last_modified and current_last_modified == cached_last_modified:
				print("[zad6] Serwer potwierdzil, ze obrazek nie zmienil sie.")
				return

			print(f"[zad6] Aktualny Last-Modified: {current_last_modified}")

		headers_for_get = dict(headers)
		headers_for_get.pop("If-Modified-Since", None)

		with socket.create_connection((TASK6_HOST, TASK6_PORT), timeout=15) as connection:
			connection.settimeout(15)
			request = _build_request("GET", TASK6_HOST, TASK6_PATH, headers_for_get)
			print(f"[zad6] C: GET {TASK6_PATH} HTTP/1.1")
			_send_http_request(connection, request)

			status_code, reason, response_headers, body = _read_http_response(connection)
			print(f"[zad6] S: HTTP/1.1 {status_code} {reason}")

			if status_code not in {200, 206}:
				raise RuntimeError(f"Unexpected HTTP status {status_code} for task 6.")

			if response_headers.get("content-encoding"):
				body = _decode_body(response_headers, body)

			output_path = _save_bytes(TASK6_OUTPUT, body)
			_save_text(TASK6_META, current_last_modified)
			print(f"[zad6] Zapisano plik: {output_path}")
			print(f"[zad6] Zapisano Last-Modified do {TASK6_META}")
			print("[zad6] Zakonczono pomyslnie.")
	except (OSError, RuntimeError, TimeoutError) as error:
		print(f"[zad6] Error: {error}")


def task_7() -> None:
	print(f"[zad7] Local server proof -> {TASK7_HOST}:{TASK7_PORT}")

	headers = {
		"User-Agent": SAFARI_703_USER_AGENT,
		"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
		"Connection": "close",
	}

	_log_request_headers("zad7", headers)

	try:
		for path in (TASK7_PATH_OK, TASK7_PATH_404):
			with socket.create_connection((TASK7_HOST, TASK7_PORT), timeout=15) as connection:
				connection.settimeout(15)
				request = _build_request("GET", TASK7_HOST, path, headers)
				print(f"[zad7] C: GET {path} HTTP/1.1")
				_send_http_request(connection, request)

				status_code, reason, response_headers, body = _read_http_response(connection)
				print(f"[zad7] S: HTTP/1.1 {status_code} {reason}")
				print(f"[zad7] Content-Type: {response_headers.get('content-type', 'brak')}")
				print(f"[zad7] Body bytes: {len(body)}")

		print("[zad7] Zakonczono pomyslnie.")
	except (OSError, RuntimeError, TimeoutError) as error:
		print(f"[zad7] Error: {error}")


def main() -> None:
	task_handlers: dict[int, Callable[[], None]] = {
		1: task_1,
		2: task_2,
		3: task_3,
		4: task_4,
		5: task_5,
		6: task_6,
		7: task_7,
	}

	any_task_enabled = False
	for task_number in range(1, 8):
		if not TASK_TOGGLES.get(task_number, False):
			continue

		any_task_enabled = True
		handler = task_handlers.get(task_number)
		if handler is None:
			print(f"[Zadanie {task_number}] Brak implementacji.")
			continue

		handler()

	if not any_task_enabled:
		print("brak taskow")


if __name__ == "__main__":
	main()
