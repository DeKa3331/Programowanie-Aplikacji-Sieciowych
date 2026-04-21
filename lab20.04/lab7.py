import socket
from email import policy
from email.parser import BytesParser
from pathlib import Path
from typing import Callable

from recvall import (
	decode_line,
	parse_stat_response,
	pop3_login,
	pop3_roundtrip,
	recv_line,
	recv_pop3_multiline,
	require_ok,
	send_pop3_command,
)

# Globalnie uzywam:
# login: student@localhost
# haslo: test123

TASK1_HOST = "127.0.0.1"
TASK1_PORT = 1110
TASK1_EMAIL = "student@localhost"

TASK2_HOST = "127.0.0.1"
TASK2_PORT = 1111
TASK2_EMAIL = "student@localhost"

TASK3_HOST = "127.0.0.1"
TASK3_PORT = 1112
TASK3_EMAIL = "student@localhost"

TASK4_HOST = "127.0.0.1"
TASK4_PORT = 1113
TASK4_EMAIL = "student@localhost"

TASK5_HOST = "127.0.0.1"
TASK5_PORT = 1114
TASK5_EMAIL = "student@localhost"

TASK6_HOST = "127.0.0.1"
TASK6_PORT = 1115
TASK6_EMAIL = "student@localhost"

TASK7_HOST = "127.0.0.1"
TASK7_PORT = 1116
TASK7_EMAIL = "student@localhost"

TASK8_HOST = "127.0.0.1"
TASK8_PORT = 1117
TASK8_EMAIL = "student@localhost"

TASK9_HOST = "127.0.0.1"
TASK9_PORT = 1118
TASK9_EMAIL = "student@localhost"

TASK10_HOST = "127.0.0.1"
TASK10_PORT = 1119
TASK10_EMAIL = "student@localhost"

TASK11_HOST = "127.0.0.1"
TASK11_PORT = 1120
TASK11_EMAIL = "student@localhost"

TASK12_HOST = "127.0.0.1"
TASK12_PORT = 1121
TASK12_EMAIL = "student@localhost"

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
	10: False,
	11: False,
	12: True,
}

def task_1() -> None:
	print(f"[zad1] POP3 STAT (liczba wiadomosci) -> {TASK1_HOST}:{TASK1_PORT}")

	email = input(f"[zad1] Login [{TASK1_EMAIL}]: ").strip() or TASK1_EMAIL
	password = input("[zad1] Haslo: ").strip()

	if not password:
		print("[zad1] Haslo jest wymagane.")
		return

	try:
		with socket.create_connection((TASK1_HOST, TASK1_PORT), timeout=15) as connection:
			connection.settimeout(15)

			greeting = decode_line(recv_line(connection))
			print(f"[zad1] S: {greeting}")
			require_ok(greeting)

			pop3_login(connection, email, password, "zad1")
			stat_response = pop3_roundtrip(connection, "STAT", "zad1")
			message_count, _ = parse_stat_response(stat_response)

			print(f"[zad1] Liczba wiadomosci w skrzynce: {message_count}")
			pop3_roundtrip(connection, "QUIT", "zad1")

		print("[zad1] Zakonczono pomyslnie.")
	except (OSError, RuntimeError, TimeoutError) as error:
		print(f"[zad1] Error: {error}")


def task_2() -> None:
	print(f"[zad2] POP3 LIST (suma bajtow) -> {TASK2_HOST}:{TASK2_PORT}")

	email = input(f"[zad2] Login [{TASK2_EMAIL}]: ").strip() or TASK2_EMAIL
	password = input("[zad2] Haslo: ").strip()

	if not password:
		print("[zad2] Haslo jest wymagane.")
		return

	try:
		with socket.create_connection((TASK2_HOST, TASK2_PORT), timeout=15) as connection:
			connection.settimeout(15)

			greeting = decode_line(recv_line(connection))
			print(f"[zad2] S: {greeting}")
			require_ok(greeting)

			pop3_login(connection, email, password, "zad2")
			stat_response = pop3_roundtrip(connection, "STAT", "zad2")
			msg_count_stat, total_octets_stat = parse_stat_response(stat_response)

			print("[zad2] C: LIST")
			send_pop3_command(connection, "LIST")
			list_header = decode_line(recv_line(connection))
			print(f"[zad2] S: {list_header}")
			require_ok(list_header)

			list_lines = [decode_line(line) for line in recv_pop3_multiline(connection)]
			total_octets_list = 0
			parsed_lines = 0

			for line in list_lines:
				parts = line.split()
				if len(parts) < 2:
					continue

				try:
					size = int(parts[1])
				except ValueError:
					continue

				parsed_lines += 1
				total_octets_list += size

			print(f"[zad2] Suma bajtow z LIST: {total_octets_list}")
			print(f"[zad2] STAT raportuje: {msg_count_stat} wiadomosci, {total_octets_stat} bajtow")

			if parsed_lines != msg_count_stat:
				print("[zad2] Uwaga: liczba wpisow LIST rozni sie od liczby wiadomosci w STAT.")

			pop3_roundtrip(connection, "QUIT", "zad2")

		print("[zad2] Zakonczono pomyslnie.")
	except (OSError, RuntimeError, TimeoutError) as error:
		print(f"[zad2] Error: {error}")


def task_3() -> None:
	print(f"[zad3] POP3 LIST (bajty kazdej wiadomosci) -> {TASK3_HOST}:{TASK3_PORT}")

	email = input(f"[zad3] Login [{TASK3_EMAIL}]: ").strip() or TASK3_EMAIL
	password = input("[zad3] Haslo: ").strip()

	if not password:
		print("[zad3] Haslo jest wymagane.")
		return

	try:
		with socket.create_connection((TASK3_HOST, TASK3_PORT), timeout=15) as connection:
			connection.settimeout(15)

			greeting = decode_line(recv_line(connection))
			print(f"[zad3] S: {greeting}")
			require_ok(greeting)

			pop3_login(connection, email, password, "zad3")

			print("[zad3] C: LIST")
			send_pop3_command(connection, "LIST")
			list_header = decode_line(recv_line(connection))
			print(f"[zad3] S: {list_header}")
			require_ok(list_header)

			list_lines = [decode_line(line) for line in recv_pop3_multiline(connection)]
			if not list_lines:
				print("[zad3] Brak wiadomosci w skrzynce.")
			else:
				for line in list_lines:
					parts = line.split()
					if len(parts) < 2:
						continue

					try:
						msg_id = int(parts[0])
						size = int(parts[1])
					except ValueError:
						continue

					print(f"[zad3] Wiadomosc {msg_id}: {size} bajtow")

			pop3_roundtrip(connection, "QUIT", "zad3")

		print("[zad3] Zakonczono pomyslnie.")
	except (OSError, RuntimeError, TimeoutError) as error:
		print(f"[zad3] Error: {error}")


def task_4() -> None:
	print(f"[zad4] POP3 RETR (najwieksza wiadomosc) -> {TASK4_HOST}:{TASK4_PORT}")

	email = input(f"[zad4] Login [{TASK4_EMAIL}]: ").strip() or TASK4_EMAIL
	password = input("[zad4] Haslo: ").strip()

	if not password:
		print("[zad4] Haslo jest wymagane.")
		return

	try:
		with socket.create_connection((TASK4_HOST, TASK4_PORT), timeout=15) as connection:
			connection.settimeout(15)

			greeting = decode_line(recv_line(connection))
			print(f"[zad4] S: {greeting}")
			require_ok(greeting)

			pop3_login(connection, email, password, "zad4")

			print("[zad4] C: LIST")
			send_pop3_command(connection, "LIST")
			list_header = decode_line(recv_line(connection))
			print(f"[zad4] S: {list_header}")
			require_ok(list_header)

			list_lines = [decode_line(line) for line in recv_pop3_multiline(connection)]
			parsed_sizes: list[tuple[int, int]] = []

			for line in list_lines:
				parts = line.split()
				if len(parts) < 2:
					continue

				try:
					msg_id = int(parts[0])
					size = int(parts[1])
				except ValueError:
					continue

				parsed_sizes.append((msg_id, size))

			if not parsed_sizes:
				print("[zad4] Brak wiadomosci do pobrania.")
				pop3_roundtrip(connection, "QUIT", "zad4")
				return

			largest_id, largest_size = max(parsed_sizes, key=lambda item: item[1])
			print(f"[zad4] Najwieksza wiadomosc: id={largest_id}, rozmiar={largest_size} bajtow")

			print(f"[zad4] C: RETR {largest_id}")
			send_pop3_command(connection, f"RETR {largest_id}")
			retr_header = decode_line(recv_line(connection))
			print(f"[zad4] S: {retr_header}")
			require_ok(retr_header)

			message_lines = [decode_line(line) for line in recv_pop3_multiline(connection)]
			print("[zad4] Tresc wiadomosci:")
			for line in message_lines:
				print(line)

			pop3_roundtrip(connection, "QUIT", "zad4")

		print("[zad4] Zakonczono pomyslnie.")
	except (OSError, RuntimeError, TimeoutError) as error:
		print(f"[zad4] Error: {error}")


def task_5() -> None:
	print(f"[zad5] POP3 DELE (najmniejsza wiadomosc) -> {TASK5_HOST}:{TASK5_PORT}")

	email = input(f"[zad5] Login [{TASK5_EMAIL}]: ").strip() or TASK5_EMAIL
	password = input("[zad5] Haslo: ").strip()

	if not password:
		print("[zad5] Haslo jest wymagane.")
		return

	try:
		with socket.create_connection((TASK5_HOST, TASK5_PORT), timeout=15) as connection:
			connection.settimeout(15)

			greeting = decode_line(recv_line(connection))
			print(f"[zad5] S: {greeting}")
			require_ok(greeting)

			pop3_login(connection, email, password, "zad5")

			print("[zad5] C: LIST")
			send_pop3_command(connection, "LIST")
			list_header = decode_line(recv_line(connection))
			print(f"[zad5] S: {list_header}")
			require_ok(list_header)

			list_lines = [decode_line(line) for line in recv_pop3_multiline(connection)]
			parsed_sizes: list[tuple[int, int]] = []

			for line in list_lines:
				parts = line.split()
				if len(parts) < 2:
					continue

				try:
					msg_id = int(parts[0])
					size = int(parts[1])
				except ValueError:
					continue

				parsed_sizes.append((msg_id, size))

			if not parsed_sizes:
				print("[zad5] Brak wiadomosci do usuniecia.")
				pop3_roundtrip(connection, "QUIT", "zad5")
				return

			smallest_id, smallest_size = min(parsed_sizes, key=lambda item: item[1])
			print(f"[zad5] Najmniejsza wiadomosc: id={smallest_id}, rozmiar={smallest_size} bajtow")

			pop3_roundtrip(connection, f"DELE {smallest_id}", "zad5")
			print(f"[zad5] Oznaczono do usuniecia wiadomosc id={smallest_id}")

			pop3_roundtrip(connection, "QUIT", "zad5")

		print("[zad5] Zakonczono pomyslnie.")
	except (OSError, RuntimeError, TimeoutError) as error:
		print(f"[zad5] Error: {error}")


def task_6() -> None:
	print(f"[zad6] POP3 client (liczba wiadomosci) -> {TASK6_HOST}:{TASK6_PORT}")

	email = input(f"[zad6] Login [{TASK6_EMAIL}]: ").strip() or TASK6_EMAIL
	password = input("[zad6] Haslo: ").strip()

	if not password:
		print("[zad6] Haslo jest wymagane.")
		return

	try:
		with socket.create_connection((TASK6_HOST, TASK6_PORT), timeout=15) as connection:
			connection.settimeout(15)

			greeting = decode_line(recv_line(connection))
			print(f"[zad6] S: {greeting}")
			require_ok(greeting)

			pop3_login(connection, email, password, "zad6")
			stat_response = pop3_roundtrip(connection, "STAT", "zad6")
			message_count, _ = parse_stat_response(stat_response)

			print(f"[zad6] Liczba wiadomosci w skrzynce: {message_count}")
			pop3_roundtrip(connection, "QUIT", "zad6")

		print("[zad6] Zakonczono pomyslnie.")
	except (OSError, RuntimeError, TimeoutError) as error:
		print(f"[zad6] Error: {error}")


def task_7() -> None:
	print(f"[zad7] POP3 client (suma bajtow) -> {TASK7_HOST}:{TASK7_PORT}")

	email = input(f"[zad7] Login [{TASK7_EMAIL}]: ").strip() or TASK7_EMAIL
	password = input("[zad7] Haslo: ").strip()

	if not password:
		print("[zad7] Haslo jest wymagane.")
		return

	try:
		with socket.create_connection((TASK7_HOST, TASK7_PORT), timeout=15) as connection:
			connection.settimeout(15)

			greeting = decode_line(recv_line(connection))
			print(f"[zad7] S: {greeting}")
			require_ok(greeting)

			pop3_login(connection, email, password, "zad7")
			stat_response = pop3_roundtrip(connection, "STAT", "zad7")
			msg_count_stat, total_octets_stat = parse_stat_response(stat_response)

			print("[zad7] C: LIST")
			send_pop3_command(connection, "LIST")
			list_header = decode_line(recv_line(connection))
			print(f"[zad7] S: {list_header}")
			require_ok(list_header)

			list_lines = [decode_line(line) for line in recv_pop3_multiline(connection)]
			total_octets_list = 0
			parsed_lines = 0

			for line in list_lines:
				parts = line.split()
				if len(parts) < 2:
					continue

				try:
					size = int(parts[1])
				except ValueError:
					continue

				parsed_lines += 1
				total_octets_list += size

			print(f"[zad7] Suma bajtow z LIST: {total_octets_list}")
			print(f"[zad7] STAT raportuje: {msg_count_stat} wiadomosci, {total_octets_stat} bajtow")

			if parsed_lines != msg_count_stat:
				print("[zad7] Uwaga: liczba wpisow LIST rozni sie od liczby wiadomosci w STAT.")

			pop3_roundtrip(connection, "QUIT", "zad7")

		print("[zad7] Zakonczono pomyslnie.")
	except (OSError, RuntimeError, TimeoutError) as error:
		print(f"[zad7] Error: {error}")


def task_8() -> None:
	print(f"[zad8] POP3 client (bajty kazdej wiadomosci) -> {TASK8_HOST}:{TASK8_PORT}")

	email = input(f"[zad8] Login [{TASK8_EMAIL}]: ").strip() or TASK8_EMAIL
	password = input("[zad8] Haslo: ").strip()

	if not password:
		print("[zad8] Haslo jest wymagane.")
		return

	try:
		with socket.create_connection((TASK8_HOST, TASK8_PORT), timeout=15) as connection:
			connection.settimeout(15)

			greeting = decode_line(recv_line(connection))
			print(f"[zad8] S: {greeting}")
			require_ok(greeting)

			pop3_login(connection, email, password, "zad8")

			print("[zad8] C: LIST")
			send_pop3_command(connection, "LIST")
			list_header = decode_line(recv_line(connection))
			print(f"[zad8] S: {list_header}")
			require_ok(list_header)

			list_lines = [decode_line(line) for line in recv_pop3_multiline(connection)]
			if not list_lines:
				print("[zad8] Brak wiadomosci w skrzynce.")
			else:
				for line in list_lines:
					parts = line.split()
					if len(parts) < 2:
						continue

					try:
						msg_id = int(parts[0])
						size = int(parts[1])
					except ValueError:
						continue

					print(f"[zad8] Wiadomosc {msg_id}: {size} bajtow")

			pop3_roundtrip(connection, "QUIT", "zad8")

		print("[zad8] Zakonczono pomyslnie.")
	except (OSError, RuntimeError, TimeoutError) as error:
		print(f"[zad8] Error: {error}")


def task_9() -> None:
	print(f"[zad9] POP3 client (tresc najwiekszej wiadomosci) -> {TASK9_HOST}:{TASK9_PORT}")

	email = input(f"[zad9] Login [{TASK9_EMAIL}]: ").strip() or TASK9_EMAIL
	password = input("[zad9] Haslo: ").strip()

	if not password:
		print("[zad9] Haslo jest wymagane.")
		return

	try:
		with socket.create_connection((TASK9_HOST, TASK9_PORT), timeout=15) as connection:
			connection.settimeout(15)

			greeting = decode_line(recv_line(connection))
			print(f"[zad9] S: {greeting}")
			require_ok(greeting)

			pop3_login(connection, email, password, "zad9")

			print("[zad9] C: LIST")
			send_pop3_command(connection, "LIST")
			list_header = decode_line(recv_line(connection))
			print(f"[zad9] S: {list_header}")
			require_ok(list_header)

			list_lines = [decode_line(line) for line in recv_pop3_multiline(connection)]
			parsed_sizes: list[tuple[int, int]] = []

			for line in list_lines:
				parts = line.split()
				if len(parts) < 2:
					continue

				try:
					msg_id = int(parts[0])
					size = int(parts[1])
				except ValueError:
					continue

				parsed_sizes.append((msg_id, size))

			if not parsed_sizes:
				print("[zad9] Brak wiadomosci do pobrania.")
				pop3_roundtrip(connection, "QUIT", "zad9")
				return

			largest_id, largest_size = max(parsed_sizes, key=lambda item: item[1])
			print(f"[zad9] Najwieksza wiadomosc: id={largest_id}, rozmiar={largest_size} bajtow")

			print(f"[zad9] C: RETR {largest_id}")
			send_pop3_command(connection, f"RETR {largest_id}")
			retr_header = decode_line(recv_line(connection))
			print(f"[zad9] S: {retr_header}")
			require_ok(retr_header)

			message_lines = [decode_line(line) for line in recv_pop3_multiline(connection)]
			print("[zad9] Tresc wiadomosci:")
			for line in message_lines:
				print(line)

			pop3_roundtrip(connection, "QUIT", "zad9")

		print("[zad9] Zakonczono pomyslnie.")
	except (OSError, RuntimeError, TimeoutError) as error:
		print(f"[zad9] Error: {error}")


def task_10() -> None:
	print(f"[zad10] POP3 client (wyswietl wszystkie wiadomosci) -> {TASK10_HOST}:{TASK10_PORT}")

	email = input(f"[zad10] Login [{TASK10_EMAIL}]: ").strip() or TASK10_EMAIL
	password = input("[zad10] Haslo: ").strip()

	if not password:
		print("[zad10] Haslo jest wymagane.")
		return

	try:
		with socket.create_connection((TASK10_HOST, TASK10_PORT), timeout=15) as connection:
			connection.settimeout(15)

			greeting = decode_line(recv_line(connection))
			print(f"[zad10] S: {greeting}")
			require_ok(greeting)

			pop3_login(connection, email, password, "zad10")

			print("[zad10] C: LIST")
			send_pop3_command(connection, "LIST")
			list_header = decode_line(recv_line(connection))
			print(f"[zad10] S: {list_header}")
			require_ok(list_header)

			list_lines = [decode_line(line) for line in recv_pop3_multiline(connection)]
			message_ids: list[int] = []

			for line in list_lines:
				parts = line.split()
				if len(parts) < 2:
					continue

				try:
					message_ids.append(int(parts[0]))
				except ValueError:
					continue

			if not message_ids:
				print("[zad10] Brak wiadomosci w skrzynce.")
				pop3_roundtrip(connection, "QUIT", "zad10")
				return

			for msg_id in message_ids:
				print(f"[zad10] C: RETR {msg_id}")
				send_pop3_command(connection, f"RETR {msg_id}")
				retr_header = decode_line(recv_line(connection))
				print(f"[zad10] S: {retr_header}")
				require_ok(retr_header)

				message_lines = [decode_line(line) for line in recv_pop3_multiline(connection)]
				print(f"[zad10] --- WIADOMOSC {msg_id} ---")
				for line in message_lines:
					print(line)

			pop3_roundtrip(connection, "QUIT", "zad10")

		print("[zad10] Zakonczono pomyslnie.")
	except (OSError, RuntimeError, TimeoutError) as error:
		print(f"[zad10] Error: {error}")


def task_11() -> None:
	print(f"[zad11] POP3 client (pobierz zalacznik obrazkowy) -> {TASK11_HOST}:{TASK11_PORT}")

	email = input(f"[zad11] Login [{TASK11_EMAIL}]: ").strip() or TASK11_EMAIL
	password = input("[zad11] Haslo: ").strip()

	if not password:
		print("[zad11] Haslo jest wymagane.")
		return

	try:
		with socket.create_connection((TASK11_HOST, TASK11_PORT), timeout=15) as connection:
			connection.settimeout(15)

			greeting = decode_line(recv_line(connection))
			print(f"[zad11] S: {greeting}")
			require_ok(greeting)

			pop3_login(connection, email, password, "zad11")

			print("[zad11] C: LIST")
			send_pop3_command(connection, "LIST")
			list_header = decode_line(recv_line(connection))
			print(f"[zad11] S: {list_header}")
			require_ok(list_header)

			list_lines = [decode_line(line) for line in recv_pop3_multiline(connection)]
			message_ids: list[int] = []

			for line in list_lines:
				parts = line.split()
				if len(parts) < 2:
					continue

				try:
					message_ids.append(int(parts[0]))
				except ValueError:
					continue

			if not message_ids:
				print("[zad11] Brak wiadomosci w skrzynce.")
				pop3_roundtrip(connection, "QUIT", "zad11")
				return

			attachment_saved = False

			for msg_id in message_ids:
				print(f"[zad11] C: RETR {msg_id}")
				send_pop3_command(connection, f"RETR {msg_id}")
				retr_header = decode_line(recv_line(connection))
				print(f"[zad11] S: {retr_header}")
				require_ok(retr_header)

				raw_lines = recv_pop3_multiline(connection)
				raw_message = b"\r\n".join(raw_lines) + b"\r\n"
				email_message = BytesParser(policy=policy.default).parsebytes(raw_message)

				for part in email_message.walk():
					if part.get_content_disposition() != "attachment":
						continue

					filename = part.get_filename()
					payload = part.get_payload(decode=True)

					if not filename or payload is None:
						continue

					output_path = Path(filename)
					output_path.write_bytes(payload)
					print(f"[zad11] Zapisano zalacznik: {output_path}")
					attachment_saved = True
					break

				if attachment_saved:
					break

			if not attachment_saved:
				print("[zad11] Nie znaleziono zalacznika w wiadomosciach.")

			pop3_roundtrip(connection, "QUIT", "zad11")

		print("[zad11] Zakonczono pomyslnie.")
	except (OSError, RuntimeError, TimeoutError) as error:
		print(f"[zad11] Error: {error}")


def task_12() -> None:
	print(f"[zad12] POP3 server test -> {TASK12_HOST}:{TASK12_PORT}")

	email = input(f"[zad12] Login [{TASK12_EMAIL}]: ").strip() or TASK12_EMAIL
	password = input("[zad12] Haslo: ").strip()

	if not password:
		print("[zad12] Haslo jest wymagane.")
		return

	try:
		with socket.create_connection((TASK12_HOST, TASK12_PORT), timeout=15) as connection:
			connection.settimeout(15)

			greeting = decode_line(recv_line(connection))
			print(f"[zad12] S: {greeting}")
			require_ok(greeting)

			pop3_login(connection, email, password, "zad12")

			stat_response = pop3_roundtrip(connection, "STAT", "zad12")
			message_count, total_octets = parse_stat_response(stat_response)
			print(f"[zad12] STAT -> wiadomosci: {message_count}, bajty: {total_octets}")

			print("[zad12] C: LIST")
			send_pop3_command(connection, "LIST")
			list_header = decode_line(recv_line(connection))
			print(f"[zad12] S: {list_header}")
			require_ok(list_header)

			list_lines = [decode_line(line) for line in recv_pop3_multiline(connection)]
			for line in list_lines:
				print(f"[zad12] LIST: {line}")

			first_id = None
			for line in list_lines:
				parts = line.split()
				if len(parts) < 2:
					continue

				try:
					first_id = int(parts[0])
					break
				except ValueError:
					continue

			if first_id is not None:
				print(f"[zad12] C: RETR {first_id}")
				send_pop3_command(connection, f"RETR {first_id}")
				retr_header = decode_line(recv_line(connection))
				print(f"[zad12] S: {retr_header}")
				require_ok(retr_header)

				message_lines = [decode_line(line) for line in recv_pop3_multiline(connection)]
				print(f"[zad12] --- WIADOMOSC {first_id} ---")
				for line in message_lines:
					print(line)

			print("[zad12] C: X-UNKNOWN-COMMAND")
			send_pop3_command(connection, "X-UNKNOWN-COMMAND")
			unknown_response = decode_line(recv_line(connection))
			print(f"[zad12] S: {unknown_response}")

			if unknown_response.startswith("-ERR"):
				print("[zad12] OK: serwer poprawnie obsluzyl nieznana komende.")
			else:
				print("[zad12] Uwaga: oczekiwano -ERR dla nieznanej komendy.")

			pop3_roundtrip(connection, "QUIT", "zad12")

		print("[zad12] Zakonczono pomyslnie.")
	except (OSError, RuntimeError, TimeoutError) as error:
		print(f"[zad12] Error: {error}")


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
		11: task_11,
		12: task_12,
	}

	any_task_enabled = False

	for task_number in range(1, 13):
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
