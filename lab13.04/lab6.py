import socket
import base64
from pathlib import Path
from typing import Callable


TASK1_HOST = "127.0.0.1"
TASK1_PORT = 2525

TASK2_HOST = "127.0.0.1"
TASK2_PORT = 2526

TASK3_HOST = "127.0.0.1"
TASK3_PORT = 2527

TASK4_HOST = "127.0.0.1"
TASK4_PORT = 2528
TASK4_ATTACHMENT_PATH = r"C:\Users\Jakub\Desktop\paradygmaty.txt" #moj losowy txt z pulpitu

TASK5_HOST = "127.0.0.1"
TASK5_PORT = 2529
TASK5_IMAGE_PATH = r"C:\Users\Jakub\Desktop\rf2.jpg"

TASK6_HOST = "127.0.0.1"
TASK6_PORT = 2530

TASK7_HOST = "127.0.0.1"
TASK7_PORT = 2531

TASK8_HOST = "127.0.0.1"
TASK8_PORT = 2532
TASK8_IMAGE_PATH = r"C:\Users\Jakub\Desktop\rf2.jpg"

TASK9_HOST = "127.0.0.1"
TASK9_PORT = 2533
TASK9_HTMLMESSAGE= """<h1>Wiadomość testowa</h1>
<p>To jest <b>pogrubiony</b>, <i>pochylony</i> i <u>podkreślony</u> tekst.</p>
<p>Sprawdzam wysyłanie wiadomości HTML przez SMTP.</p>
<ul>
  <li>punkt 1</li>
  <li>punkt 2</li>
  <li>punkt 3</li>
</ul>"""

TASK10_HOST = "127.0.0.1"
TASK10_PORT = 2534
TASK10_MAIL_FROM = "test@localhost"
TASK10_RCPT_TO = "odbiorca@localhost"
TASK10_SUBJECT = "zad10 test"
TASK10_BODY = "To jest test serwera SMTP z zadania 10."


TASK_TOGGLES: dict[int, bool] = {
	1: False,
	2: False,
	3: False,
	4: False,
	5: False,
	6: False,
	7: False,
	8: False,
	9: False,
	10: True,
}


def read_smtp_response(reader: socket.SocketIO) -> tuple[int, list[str]]:
	lines: list[str] = []

	while True:
		raw_line = reader.readline()
		if not raw_line:
			raise OSError("Server closed the connection while sending a response.")

		line = raw_line.decode("utf-8", errors="replace").rstrip("\r\n")
		lines.append(line)

		if len(line) >= 4 and line[:3].isdigit() and line[3] == " ":
			return int(line[:3]), lines


def send_smtp_command(writer: socket.SocketIO, command: str) -> None:
	writer.write((command + "\r\n").encode("utf-8"))
	writer.flush()


def require_code(actual_code: int, expected_codes: set[int], response_lines: list[str]) -> None:
	if actual_code not in expected_codes:
		text = "\n".join(response_lines)
		raise RuntimeError(f"Unexpected SMTP code {actual_code}, expected {sorted(expected_codes)}.\n{text}")


def smtp_roundtrip(
	reader: socket.SocketIO,
	writer: socket.SocketIO,
	command: str,
	expected_codes: set[int],
	log_prefix: str,
) -> tuple[int, list[str]]:
	print(f"[{log_prefix}] C: {command}")
	send_smtp_command(writer, command)
	code, lines = read_smtp_response(reader)
	for line in lines:
		print(f"[{log_prefix}] S: {line}")
	require_code(code, expected_codes, lines)
	return code, lines


def open_smtp_session(host: str, port: int, log_prefix: str) -> tuple[socket.socket, socket.SocketIO, socket.SocketIO]:
	connection = socket.create_connection((host, port), timeout=15)
	connection.settimeout(15)
	reader = connection.makefile("rb")
	writer = connection.makefile("wb")

	code, lines = read_smtp_response(reader)
	require_code(code, {220}, lines)
	for line in lines:
		print(f"[{log_prefix}] S: {line}")

	smtp_roundtrip(reader, writer, "EHLO localhost", {250}, log_prefix)
	return connection, reader, writer


def task_1() -> None:
	print(f"[zad1] SMTP client -> {TASK1_HOST}:{TASK1_PORT}")

	mail_from = input("[zad1] MAIL FROM: ").strip()
	rcpt_to = input("[zad1] RCPT TO: ").strip()
	subject = input("[zad1] Subject: ").strip() or "test"
	body = input("[zad1] Message body: ").strip() or "test"

	if not mail_from or not rcpt_to:
		print("[zad1] MAIL FROM i RCPT TO sa wymagane.")
		return

	try:
		with socket.create_connection((TASK1_HOST, TASK1_PORT), timeout=15) as connection:
			connection.settimeout(15)
			reader = connection.makefile("rb")
			writer = connection.makefile("wb")

			code, lines = read_smtp_response(reader)
			require_code(code, {220}, lines)
			for line in lines:
				print(f"[zad1] S: {line}")

			smtp_roundtrip(reader, writer, "EHLO localhost", {250}, "zad1")
			smtp_roundtrip(reader, writer, f"MAIL FROM:<{mail_from}>", {250, 251}, "zad1")
			smtp_roundtrip(reader, writer, f"RCPT TO:<{rcpt_to}>", {250, 251}, "zad1")
			smtp_roundtrip(reader, writer, "DATA", {354}, "zad1")

			message_data = (
				f"From: {mail_from}\r\n"
				f"To: {rcpt_to}\r\n"
				f"Subject: {subject}\r\n"
				"\r\n"
				f"{body}\r\n"
				"."
			)

			smtp_roundtrip(reader, writer, message_data, {250}, "zad1")
			smtp_roundtrip(reader, writer, "QUIT", {221}, "zad1")

		print("[zad1] SMTP flow finished successfully.")
	except (OSError, RuntimeError, TimeoutError) as error:
		print(f"[zad1] Error: {error}")


def task_2() -> None:
	print(f"[zad2] SMTP multi-recipient -> {TASK2_HOST}:{TASK2_PORT}")

	mail_from = input("[zad2] MAIL FROM: ").strip()
	rcpt_raw = input("[zad2] RCPT TO (oddziel przecinkami): ").strip()
	subject = input("[zad2] Subject: ").strip() or "test multi"
	body = input("[zad2] Message body: ").strip() or "test multi body"

	recipients = [item.strip() for item in rcpt_raw.split(",") if item.strip()]
	if not mail_from or not recipients:
		print("[zad2] MAIL FROM i min. 1 odbiorca sa wymagane.")
		return

	try:
		with socket.create_connection((TASK2_HOST, TASK2_PORT), timeout=15) as connection:
			connection.settimeout(15)
			reader = connection.makefile("rb")
			writer = connection.makefile("wb")

			code, lines = read_smtp_response(reader)
			require_code(code, {220}, lines)
			for line in lines:
				print(f"[zad2] S: {line}")

			smtp_roundtrip(reader, writer, "EHLO localhost", {250}, "zad2")
			smtp_roundtrip(reader, writer, f"MAIL FROM:<{mail_from}>", {250, 251}, "zad2")

			for recipient in recipients:
				smtp_roundtrip(reader, writer, f"RCPT TO:<{recipient}>", {250, 251}, "zad2")

			smtp_roundtrip(reader, writer, "DATA", {354}, "zad2")

			header_to = ", ".join(recipients)
			message_data = (
				f"From: {mail_from}\r\n"
				f"To: {header_to}\r\n"
				f"Subject: {subject}\r\n"
				"\r\n"
				f"{body}\r\n"
				"."
			)

			smtp_roundtrip(reader, writer, message_data, {250}, "zad2")
			smtp_roundtrip(reader, writer, "QUIT", {221}, "zad2")

		print(f"[zad2] SMTP flow finished successfully. Odbiorcy: {len(recipients)}")
	except (OSError, RuntimeError, TimeoutError) as error:
		print(f"[zad2] Error: {error}")


def task_3() -> None:
	print(f"[zad3] SMTP spoof demo -> {TASK3_HOST}:{TASK3_PORT}")

	envelope_from = input("[zad3] MAIL FROM (envelope): ").strip()
	header_from = input("[zad3] Header From: ").strip()
	rcpt_to = input("[zad3] RCPT TO: ").strip()
	subject = input("[zad3] Subject: ").strip() or "spoof demo"
	body = input("[zad3] Message body: ").strip() or "spoof demo body"

	if not envelope_from or not header_from or not rcpt_to:
		print("[zad3] MAIL FROM, Header From i RCPT TO sa wymagane.")
		return

	try:
		with socket.create_connection((TASK3_HOST, TASK3_PORT), timeout=15) as connection:
			connection.settimeout(15)
			reader = connection.makefile("rb")
			writer = connection.makefile("wb")

			code, lines = read_smtp_response(reader)
			require_code(code, {220}, lines)
			for line in lines:
				print(f"[zad3] S: {line}")

			smtp_roundtrip(reader, writer, "EHLO localhost", {250}, "zad3")
			smtp_roundtrip(reader, writer, f"MAIL FROM:<{envelope_from}>", {250, 251}, "zad3")
			smtp_roundtrip(reader, writer, f"RCPT TO:<{rcpt_to}>", {250, 251}, "zad3")
			smtp_roundtrip(reader, writer, "DATA", {354}, "zad3")

			message_data = (
				f"From: {header_from}\r\n"
				f"To: {rcpt_to}\r\n"
				f"Subject: {subject}\r\n"
				"\r\n"
				f"{body}\r\n"
				"."
			)

			smtp_roundtrip(reader, writer, message_data, {250}, "zad3")
			smtp_roundtrip(reader, writer, "QUIT", {221}, "zad3")

		print("[zad3] SMTP spoof demo finished successfully.")
	except (OSError, RuntimeError, TimeoutError) as error:
		print(f"[zad3] Error: {error}")


def task_4() -> None:
	print(f"[zad4] SMTP MIME attachment -> {TASK4_HOST}:{TASK4_PORT}")

	mail_from = input("[zad4] MAIL FROM: ").strip()
	rcpt_to = input("[zad4] RCPT TO: ").strip()
	subject = input("[zad4] Subject: ").strip() or "mime attachment"
	body = input("[zad4] Message body: ").strip() or "Wiadomosc z zalacznikiem."
	# attachment_path = input("[zad4] Sciezka do pliku tekstowego: ").strip()
	attachment_path = TASK4_ATTACHMENT_PATH

	if not mail_from or not rcpt_to or not attachment_path:
		print("[zad4] MAIL FROM, RCPT TO i sciezka pliku sa wymagane.")
		return

	try:
		file_path = Path(attachment_path)
		file_data = file_path.read_bytes()
		file_b64 = base64.b64encode(file_data).decode("ascii")
		file_name = file_path.name
	except OSError as error:
		print(f"[zad4] Blad odczytu pliku: {error}")
		return

	boundary = "----PAS-LAB6-BOUNDARY-001"
	message_data = (
		f"From: {mail_from}\r\n"
		f"To: {rcpt_to}\r\n"
		f"Subject: {subject}\r\n"
		"MIME-Version: 1.0\r\n"
		f"Content-Type: multipart/mixed; boundary=\"{boundary}\"\r\n"
		"\r\n"
		f"--{boundary}\r\n"
		"Content-Type: text/plain; charset=utf-8\r\n"
		"\r\n"
		f"{body}\r\n"
		f"--{boundary}\r\n"
		f"Content-Type: text/plain; name=\"{file_name}\"\r\n"
		"Content-Transfer-Encoding: base64\r\n"
		f"Content-Disposition: attachment; filename=\"{file_name}\"\r\n"
		"\r\n"
		f"{file_b64}\r\n"
		f"--{boundary}--\r\n"
		"."
	)

	try:
		with socket.create_connection((TASK4_HOST, TASK4_PORT), timeout=15) as connection:
			connection.settimeout(15)
			reader = connection.makefile("rb")
			writer = connection.makefile("wb")

			code, lines = read_smtp_response(reader)
			require_code(code, {220}, lines)
			for line in lines:
				print(f"[zad4] S: {line}")

			smtp_roundtrip(reader, writer, "EHLO localhost", {250}, "zad4")
			smtp_roundtrip(reader, writer, f"MAIL FROM:<{mail_from}>", {250, 251}, "zad4")
			smtp_roundtrip(reader, writer, f"RCPT TO:<{rcpt_to}>", {250, 251}, "zad4")
			smtp_roundtrip(reader, writer, "DATA", {354}, "zad4")
			smtp_roundtrip(reader, writer, message_data, {250}, "zad4")
			smtp_roundtrip(reader, writer, "QUIT", {221}, "zad4")

		print(f"[zad4] SMTP MIME flow finished successfully. Zalacznik: {file_name}")
	except (OSError, RuntimeError, TimeoutError) as error:
		print(f"[zad4] Error: {error}")


def task_5() -> None:
	print(f"[zad5] SMTP image attachment -> {TASK5_HOST}:{TASK5_PORT}")

	mail_from = input("[zad5] MAIL FROM: ").strip()
	rcpt_to = input("[zad5] RCPT TO: ").strip()
	subject = input("[zad5] Subject: ").strip() or "image attachment"
	body = input("[zad5] Message body: ").strip() or "Wiadomosc z zalacznikiem obrazkowym."
	image_path = input(f"[zad5] Sciezka do obrazka [{TASK5_IMAGE_PATH}]: ").strip() or TASK5_IMAGE_PATH

	if not mail_from or not rcpt_to or not image_path:
		print("[zad5] MAIL FROM, RCPT TO i sciezka obrazka sa wymagane.")
		return

	try:
		file_path = Path(image_path)
		file_data = file_path.read_bytes()
		file_b64 = base64.b64encode(file_data).decode("ascii")
		file_name = file_path.name
		ext = file_path.suffix.lower()
		if ext in {".jpg", ".jpeg"}:
			image_type = "image/jpeg"
		elif ext == ".png":
			image_type = "image/png"
		elif ext == ".gif":
			image_type = "image/gif"
		else:
			image_type = "application/octet-stream"
	except OSError as error:
		print(f"[zad5] Blad odczytu pliku: {error}")
		return

	boundary = "----PAS-LAB6-BOUNDARY-IMG-001"
	message_data = (
		f"From: {mail_from}\r\n"
		f"To: {rcpt_to}\r\n"
		f"Subject: {subject}\r\n"
		"MIME-Version: 1.0\r\n"
		f"Content-Type: multipart/mixed; boundary=\"{boundary}\"\r\n"
		"\r\n"
		f"--{boundary}\r\n"
		"Content-Type: text/plain; charset=utf-8\r\n"
		"\r\n"
		f"{body}\r\n"
		f"--{boundary}\r\n"
		f"Content-Type: {image_type}; name=\"{file_name}\"\r\n"
		"Content-Transfer-Encoding: base64\r\n"
		f"Content-Disposition: attachment; filename=\"{file_name}\"\r\n"
		"\r\n"
		f"{file_b64}\r\n"
		f"--{boundary}--\r\n"
		"."
	)

	try:
		with socket.create_connection((TASK5_HOST, TASK5_PORT), timeout=15) as connection:
			connection.settimeout(15)
			reader = connection.makefile("rb")
			writer = connection.makefile("wb")

			code, lines = read_smtp_response(reader)
			require_code(code, {220}, lines)
			for line in lines:
				print(f"[zad5] S: {line}")

			smtp_roundtrip(reader, writer, "EHLO localhost", {250}, "zad5")
			smtp_roundtrip(reader, writer, f"MAIL FROM:<{mail_from}>", {250, 251}, "zad5")
			smtp_roundtrip(reader, writer, f"RCPT TO:<{rcpt_to}>", {250, 251}, "zad5")
			smtp_roundtrip(reader, writer, "DATA", {354}, "zad5")
			smtp_roundtrip(reader, writer, message_data, {250}, "zad5")
			smtp_roundtrip(reader, writer, "QUIT", {221}, "zad5")

		print(f"[zad5] SMTP MIME image flow finished successfully. Zalacznik: {file_name}")
	except (OSError, RuntimeError, TimeoutError) as error:
		print(f"[zad5] Error: {error}")


def task_6() -> None:
	print(f"[zad6] SMTP interactive client -> {TASK6_HOST}:{TASK6_PORT}")

	mail_from = input("[zad6] MAIL FROM: ").strip()
	rcpt_raw = input("[zad6] RCPT TO (oddziel przecinkami): ").strip()
	subject = input("[zad6] Subject: ").strip() or "interactive mail"
	body = input("[zad6] Message body: ").strip() or "interactive mail body"

	recipients = [item.strip() for item in rcpt_raw.split(",") if item.strip()]
	if not mail_from or not recipients:
		print("[zad6] MAIL FROM i min. 1 odbiorca sa wymagane.")
		return

	try:
		with socket.create_connection((TASK6_HOST, TASK6_PORT), timeout=15) as connection:
			connection.settimeout(15)
			reader = connection.makefile("rb")
			writer = connection.makefile("wb")

			code, lines = read_smtp_response(reader)
			require_code(code, {220}, lines)
			for line in lines:
				print(f"[zad6] S: {line}")

			smtp_roundtrip(reader, writer, "EHLO localhost", {250}, "zad6")
			smtp_roundtrip(reader, writer, f"MAIL FROM:<{mail_from}>", {250, 251}, "zad6")

			for recipient in recipients:
				smtp_roundtrip(reader, writer, f"RCPT TO:<{recipient}>", {250, 251}, "zad6")

			smtp_roundtrip(reader, writer, "DATA", {354}, "zad6")

			header_to = ", ".join(recipients)
			message_data = (
				f"From: {mail_from}\r\n"
				f"To: {header_to}\r\n"
				f"Subject: {subject}\r\n"
				"\r\n"
				f"{body}\r\n"
				"."
			)

			smtp_roundtrip(reader, writer, message_data, {250}, "zad6")
			smtp_roundtrip(reader, writer, "QUIT", {221}, "zad6")

		print(f"[zad6] SMTP interactive flow finished successfully. Odbiorcy: {len(recipients)}")
	except (OSError, RuntimeError, TimeoutError) as error:
		print(f"[zad6] Error: {error}")


def task_7() -> None:
	print(f"[zad7] SMTP interactive text attachment -> {TASK7_HOST}:{TASK7_PORT}")

	mail_from = input("[zad7] MAIL FROM: ").strip()
	rcpt_raw = input("[zad7] RCPT TO (oddziel przecinkami): ").strip()
	subject = input("[zad7] Subject: ").strip() or "interactive text attachment"
	body = input("[zad7] Message body: ").strip() or "Wiadomosc z tekstowym zalacznikiem."
	attachment_path = input("[zad7] Sciezka do pliku tekstowego: ").strip()

	recipients = [item.strip() for item in rcpt_raw.split(",") if item.strip()]
	if not mail_from or not recipients or not attachment_path:
		print("[zad7] MAIL FROM, min. 1 odbiorca i sciezka pliku sa wymagane.")
		return

	try:
		file_path = Path(attachment_path)
		file_data = file_path.read_bytes()
		file_b64 = base64.b64encode(file_data).decode("ascii")
		file_name = file_path.name
	except OSError as error:
		print(f"[zad7] Blad odczytu pliku: {error}")
		return

	boundary = "----PAS-LAB6-BOUNDARY-TXT-001"
	header_to = ", ".join(recipients)
	message_data = (
		f"From: {mail_from}\r\n"
		f"To: {header_to}\r\n"
		f"Subject: {subject}\r\n"
		"MIME-Version: 1.0\r\n"
		f"Content-Type: multipart/mixed; boundary=\"{boundary}\"\r\n"
		"\r\n"
		f"--{boundary}\r\n"
		"Content-Type: text/plain; charset=utf-8\r\n"
		"\r\n"
		f"{body}\r\n"
		f"--{boundary}\r\n"
		f"Content-Type: text/plain; name=\"{file_name}\"\r\n"
		"Content-Transfer-Encoding: base64\r\n"
		f"Content-Disposition: attachment; filename=\"{file_name}\"\r\n"
		"\r\n"
		f"{file_b64}\r\n"
		f"--{boundary}--\r\n"
		"."
	)

	try:
		with socket.create_connection((TASK7_HOST, TASK7_PORT), timeout=15) as connection:
			connection.settimeout(15)
			reader = connection.makefile("rb")
			writer = connection.makefile("wb")

			code, lines = read_smtp_response(reader)
			require_code(code, {220}, lines)
			for line in lines:
				print(f"[zad7] S: {line}")

			smtp_roundtrip(reader, writer, "EHLO localhost", {250}, "zad7")
			smtp_roundtrip(reader, writer, f"MAIL FROM:<{mail_from}>", {250, 251}, "zad7")

			for recipient in recipients:
				smtp_roundtrip(reader, writer, f"RCPT TO:<{recipient}>", {250, 251}, "zad7")

			smtp_roundtrip(reader, writer, "DATA", {354}, "zad7")
			smtp_roundtrip(reader, writer, message_data, {250}, "zad7")
			smtp_roundtrip(reader, writer, "QUIT", {221}, "zad7")

		print(f"[zad7] SMTP interactive attachment flow finished successfully. Zalacznik: {file_name}")
	except (OSError, RuntimeError, TimeoutError) as error:
		print(f"[zad7] Error: {error}")


def task_8() -> None:
	print(f"[zad8] SMTP image attachment -> {TASK8_HOST}:{TASK8_PORT}")

	mail_from = input("[zad8] MAIL FROM: ").strip()
	rcpt_raw = input("[zad8] RCPT TO (oddziel przecinkami): ").strip()
	subject = input("[zad8] Subject: ").strip() or "image attachment"
	body = input("[zad8] Message body: ").strip() or "Wiadomosc z zalacznikiem obrazkowym."
	image_path = input(f"[zad8] Sciezka do obrazka [{TASK8_IMAGE_PATH}]: ").strip() or TASK8_IMAGE_PATH

	recipients = [item.strip() for item in rcpt_raw.split(",") if item.strip()]
	if not mail_from or not recipients or not image_path:
		print("[zad8] MAIL FROM, min. 1 odbiorca i sciezka obrazka sa wymagane.")
		return

	try:
		file_path = Path(image_path)
		file_data = file_path.read_bytes()
		file_b64 = base64.b64encode(file_data).decode("ascii")
		file_name = file_path.name
		ext = file_path.suffix.lower()
		if ext in {".jpg", ".jpeg"}:
			image_type = "image/jpeg"
		elif ext == ".png":
			image_type = "image/png"
		elif ext == ".gif":
			image_type = "image/gif"
		else:
			image_type = "application/octet-stream"
	except OSError as error:
		print(f"[zad8] Blad odczytu pliku: {error}")
		return

	boundary = "----PAS-LAB6-BOUNDARY-IMG-001"
	header_to = ", ".join(recipients)
	message_data = (
		f"From: {mail_from}\r\n"
		f"To: {header_to}\r\n"
		f"Subject: {subject}\r\n"
		"MIME-Version: 1.0\r\n"
		f"Content-Type: multipart/mixed; boundary=\"{boundary}\"\r\n"
		"\r\n"
		f"--{boundary}\r\n"
		"Content-Type: text/plain; charset=utf-8\r\n"
		"\r\n"
		f"{body}\r\n"
		f"--{boundary}\r\n"
		f"Content-Type: {image_type}; name=\"{file_name}\"\r\n"
		"Content-Transfer-Encoding: base64\r\n"
		f"Content-Disposition: attachment; filename=\"{file_name}\"\r\n"
		"\r\n"
		f"{file_b64}\r\n"
		f"--{boundary}--\r\n"
		"."
	)

	try:
		with socket.create_connection((TASK8_HOST, TASK8_PORT), timeout=15) as connection:
			connection.settimeout(15)
			reader = connection.makefile("rb")
			writer = connection.makefile("wb")

			code, lines = read_smtp_response(reader)
			require_code(code, {220}, lines)
			for line in lines:
				print(f"[zad8] S: {line}")

			smtp_roundtrip(reader, writer, "EHLO localhost", {250}, "zad8")
			smtp_roundtrip(reader, writer, f"MAIL FROM:<{mail_from}>", {250, 251}, "zad8")
			for recipient in recipients:
				smtp_roundtrip(reader, writer, f"RCPT TO:<{recipient}>", {250, 251}, "zad8")
			smtp_roundtrip(reader, writer, "DATA", {354}, "zad8")
			smtp_roundtrip(reader, writer, message_data, {250}, "zad8")
			smtp_roundtrip(reader, writer, "QUIT", {221}, "zad8")

		print(f"[zad8] SMTP MIME image flow finished successfully. Zalacznik: {file_name}")
	except (OSError, RuntimeError, TimeoutError) as error:
		print(f"[zad8] Error: {error}")


def task_9() -> None:
	print(f"[zad9] SMTP HTML mail -> {TASK9_HOST}:{TASK9_PORT}")

	mail_from = input("[zad9] MAIL FROM: ").strip()
	rcpt_raw = input("[zad9] RCPT TO (oddziel przecinkami): ").strip()
	subject = input("[zad9] Subject: ").strip() or "html mail"
	# html_body = input("[zad9] HTML body: ").strip() or "<b>pogrubienie</b> <i>pochylenie</i> <u>podkreslenie</u>"
	html_body = TASK9_HTMLMESSAGE

	recipients = [item.strip() for item in rcpt_raw.split(",") if item.strip()]
	if not mail_from or not recipients:
		print("[zad9] MAIL FROM i min. 1 odbiorca sa wymagane.")
		return

	header_to = ", ".join(recipients)
	message_data = (
		f"From: {mail_from}\r\n"
		f"To: {header_to}\r\n"
		f"Subject: {subject}\r\n"
		"MIME-Version: 1.0\r\n"
		"Content-Type: text/html; charset=utf-8\r\n"
		"\r\n"
		f"<html><body>{html_body}</body></html>\r\n"
		"."
	)

	try:
		with socket.create_connection((TASK9_HOST, TASK9_PORT), timeout=15) as connection:
			connection.settimeout(15)
			reader = connection.makefile("rb")
			writer = connection.makefile("wb")

			code, lines = read_smtp_response(reader)
			require_code(code, {220}, lines)
			for line in lines:
				print(f"[zad9] S: {line}")

			smtp_roundtrip(reader, writer, "EHLO localhost", {250}, "zad9")
			smtp_roundtrip(reader, writer, f"MAIL FROM:<{mail_from}>", {250, 251}, "zad9")
			for recipient in recipients:
				smtp_roundtrip(reader, writer, f"RCPT TO:<{recipient}>", {250, 251}, "zad9")
			smtp_roundtrip(reader, writer, "DATA", {354}, "zad9")
			smtp_roundtrip(reader, writer, message_data, {250}, "zad9")
			smtp_roundtrip(reader, writer, "QUIT", {221}, "zad9")

		print("[zad9] SMTP HTML flow finished successfully.")
	except (OSError, RuntimeError, TimeoutError) as error:
		print(f"[zad9] Error: {error}")


def task_10() -> None:
	print(f"[zad10] SMTP simulation test -> {TASK10_HOST}:{TASK10_PORT}")

	try:
		with socket.create_connection((TASK10_HOST, TASK10_PORT), timeout=15) as connection:
			connection.settimeout(15)
			reader = connection.makefile("rb")
			writer = connection.makefile("wb")

			code, lines = read_smtp_response(reader)
			require_code(code, {220}, lines)
			for line in lines:
				print(f"[zad10] S: {line}")

			smtp_roundtrip(reader, writer, "EHLO localhost", {250}, "zad10")
			smtp_roundtrip(reader, writer, "NOOP", {250}, "zad10")
			smtp_roundtrip(reader, writer, f"MAIL FROM:<{TASK10_MAIL_FROM}>", {250, 251}, "zad10")
			smtp_roundtrip(reader, writer, f"RCPT TO:<{TASK10_RCPT_TO}>", {250, 251}, "zad10")
			smtp_roundtrip(reader, writer, "DATA", {354}, "zad10")

			message_data = (
				f"From: {TASK10_MAIL_FROM}\r\n"
				f"To: {TASK10_RCPT_TO}\r\n"
				f"Subject: {TASK10_SUBJECT}\r\n"
				"\r\n"
				f"{TASK10_BODY}\r\n"
				"."
			)

			smtp_roundtrip(reader, writer, message_data, {250}, "zad10")
			smtp_roundtrip(reader, writer, "RSET", {250}, "zad10")
			smtp_roundtrip(reader, writer, "X-UNKNOWN-COMMAND", {502}, "zad10")
			smtp_roundtrip(reader, writer, "QUIT", {221}, "zad10")

		print("[zad10] SMTP simulation test finished successfully.")
	except (OSError, RuntimeError, TimeoutError) as error:
		print(f"[zad10] Error: {error}")


def main() -> None:
	task_handlers: dict[int, Callable[[], None]] = {
		1: task_1,
		2: task_2,
		3: task_3,
		4: task_4,
		5: task_5,
		6: task_6,
		7: task_7,
		8: task_8,
		9: task_9,
		10: task_10,
	}

	any_task_enabled = False

	for task_number in range(1, 11):
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
