import socket
from typing import Callable


TASK13_HOST = "127.0.0.1"
TASK13_PORT = 2909
TASK13_UDP_HEX = (
	"ed 74 0b 55 00 24 ef fd 70 72 6f 67 72 61 "
	"6d 6d 69 6e 67 20 69 6e 20 70 79 74 68 6f "
	"6e 20 69 73 20 66 75 6e"
)

TASK14_HOST = "127.0.0.1"
TASK14_PORT = 2910
TASK14_TCP_HEX = (
	"0b 54 89 8b 1f 9a 18 ec bb b1 64 f2 80 18 "
	"00 e3 67 71 00 00 01 01 08 0a 02 c1 a4 ee "
	"00 1a 4c ee 68 65 6c 6c 6f 20 3a 29"
)

TASK15_HOST = "127.0.0.1"
TASK15_PORT = 2911
TASK15_IP_HEX = (
	"45 00 00 4e f7 fa 40 00 38 06 9d 33 d4 b6 18 1b "
	"c0 a8 00 02 0b 54 b9 a6 fb f9 3c 57 c1 0a 06 c1 "
	"80 18 00 e3 ce 9c 00 00 01 01 08 0a 03 a6 eb 01 "
	"00 0b f8 e5 6e 65 74 77 6f 72 6b 20 70 72 6f 67 "
	"72 61 6d 6d 69 6e 67 20 69 73 20 66 75 6e"
)


TASK_TOGGLES: dict[int, bool] = {
	13: False,
	14: False,
	15: True,
	16: False,
}


def task_13() -> None:
	def parse_udp_datagram(hex_payload: str) -> tuple[int, int, bytes]:
		raw = bytes.fromhex(hex_payload)
		if len(raw) < 8:
			raise ValueError("Datagram UDP musi mieć co najmniej 8 bajtów nagłówka.")

		src_port = int.from_bytes(raw[0:2], byteorder="big")
		dst_port = int.from_bytes(raw[2:4], byteorder="big")
		total_len = int.from_bytes(raw[4:6], byteorder="big")

		if total_len < 8 or total_len > len(raw):
			raise ValueError("Niepoprawne pole length w nagłówku UDP.")

		data = raw[8:total_len]
		return src_port, dst_port, data

	try:
		src_port, dst_port, data_bytes = parse_udp_datagram(TASK13_UDP_HEX)
		data_text = data_bytes.decode("ascii")
	except (ValueError, UnicodeDecodeError) as error:
		print(f"[Zadanie 13] Błąd parsowania datagramu: {error}")
		return

	print(f"[Zadanie 13] Port źródłowy: {src_port}")
	print(f"[Zadanie 13] Port docelowy: {dst_port}")
	print(f"[Zadanie 13] Dane ({len(data_bytes)} bajtów): {data_text}")

	message = f"zad13odp;src;{src_port};dst;{dst_port};data;{data_text}"
	print(f"[Zadanie 13] Wiadomość: {message}")
	print(f"[Zadanie 13] Wysyłka do: {TASK13_HOST}:{TASK13_PORT}")

	try:
		with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
			sock.settimeout(5)
			sock.sendto(message.encode("utf-8"), (TASK13_HOST, TASK13_PORT))
			response, _ = sock.recvfrom(4096)

		print(f"[Zadanie 13] Odpowiedź serwera: {response.decode('utf-8', errors='replace')}")
	except ConnectionResetError:
		print("[Zadanie 13] Brak działającego serwera UDP na wskazanym porcie (WinError 10054).")
		print("[Zadanie 13] Sprawdź czy serwer weryfikujący działa na wskazanym adresie i porcie.")
	except OSError as error:
		print(f"[Zadanie 13] Błąd połączenia/komunikacji: {error}")


def task_14() -> None:
	def parse_tcp_segment(hex_payload: str) -> tuple[int, int, bytes]:
		raw = bytes.fromhex(hex_payload)
		if len(raw) < 20:
			raise ValueError("Segment TCP musi mieć co najmniej 20 bajtów nagłówka.")

		src_port = int.from_bytes(raw[0:2], byteorder="big")
		dst_port = int.from_bytes(raw[2:4], byteorder="big")
		data_offset = (raw[12] >> 4)  # górne 4 bity bajtu 12
		header_len = data_offset * 4

		if header_len < 20 or header_len > len(raw):
			raise ValueError("Niepoprawne pole data offset w nagłówku TCP.")

		data = raw[header_len:]
		return src_port, dst_port, data

	try:
		src_port, dst_port, data_bytes = parse_tcp_segment(TASK14_TCP_HEX)
		data_text = data_bytes.decode("ascii")
	except (ValueError, UnicodeDecodeError) as error:
		print(f"[Zadanie 14] Błąd parsowania segmentu: {error}")
		return

	print(f"[Zadanie 14] Port źródłowy: {src_port}")
	print(f"[Zadanie 14] Port docelowy: {dst_port}")
	print(f"[Zadanie 14] Dane ({len(data_bytes)} bajtów): {data_text}")

	message = f"zad14odp;src;{src_port};dst;{dst_port};data;{data_text}"
	print(f"[Zadanie 14] Wiadomość: {message}")
	print(f"[Zadanie 14] Wysyłka do: {TASK14_HOST}:{TASK14_PORT}")

	try:
		with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
			sock.settimeout(5)
			sock.sendto(message.encode("utf-8"), (TASK14_HOST, TASK14_PORT))
			response, _ = sock.recvfrom(4096)

		print(f"[Zadanie 14] Odpowiedź serwera: {response.decode('utf-8', errors='replace')}")
	except ConnectionResetError:
		print("[Zadanie 14] Brak działającego serwera UDP na wskazanym porcie (WinError 10054).")
	except OSError as error:
		print(f"[Zadanie 14] Błąd połączenia/komunikacji: {error}")


def task_15() -> None:
	def parse_ip_packet(hex_payload: str) -> tuple[int, str, str, int, int, int, bytes]:
		raw = bytes.fromhex(hex_payload)
		if len(raw) < 20:
			raise ValueError("Pakiet IP musi mieć co najmniej 20 bajtów nagłówka.")

		version = raw[0] >> 4
		ip_header_len = (raw[0] & 0x0F) * 4
		protocol = raw[9]
		src_ip = ".".join(str(b) for b in raw[12:16])
		dst_ip = ".".join(str(b) for b in raw[16:20])

		transport = raw[ip_header_len:]
		if len(transport) < 20:
			raise ValueError("Za krótki segment transportowy.")

		src_port = int.from_bytes(transport[0:2], byteorder="big")
		dst_port = int.from_bytes(transport[2:4], byteorder="big")

		if protocol == 6:  # TCP
			tcp_data_offset = (transport[12] >> 4) * 4
			data = transport[tcp_data_offset:]
		elif protocol == 17:  # UDP
			udp_len = int.from_bytes(transport[4:6], byteorder="big")
			data = transport[8:udp_len]
		else:
			data = transport[20:]

		return version, src_ip, dst_ip, protocol, src_port, dst_port, data

	try:
		version, src_ip, dst_ip, protocol, src_port, dst_port, data_bytes = parse_ip_packet(TASK15_IP_HEX)
		data_text = data_bytes.decode("ascii")
	except (ValueError, UnicodeDecodeError) as error:
		print(f"[Zadanie 15] Błąd parsowania pakietu: {error}")
		return

	print(f"[Zadanie 15] Wersja IP: {version}")
	print(f"[Zadanie 15] Źródłowy IP: {src_ip}")
	print(f"[Zadanie 15] Docelowy IP: {dst_ip}")
	print(f"[Zadanie 15] Protokół: {protocol}")
	print(f"[Zadanie 15] Port źródłowy: {src_port}")
	print(f"[Zadanie 15] Port docelowy: {dst_port}")
	print(f"[Zadanie 15] Dane ({len(data_bytes)} bajtów): {data_text}")

	msg_a = f"zad15odpA;ver;{version};srcip;{src_ip};dstip;{dst_ip};type;{protocol}"
	print(f"[Zadanie 15] Wiadomość A: {msg_a}")

	try:
		with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
			sock.settimeout(5)

			sock.sendto(msg_a.encode("utf-8"), (TASK15_HOST, TASK15_PORT))
			response_a, _ = sock.recvfrom(4096)
			answer_a = response_a.decode("utf-8", errors="replace")
			print(f"[Zadanie 15] Odpowiedź A: {answer_a}")

			if answer_a == "TAK":
				msg_b = f"zad15odpB;srcport;{src_port};dstport;{dst_port};data;{data_text}"
				print(f"[Zadanie 15] Wiadomość B: {msg_b}")
				sock.sendto(msg_b.encode("utf-8"), (TASK15_HOST, TASK15_PORT))
				response_b, _ = sock.recvfrom(4096)
				print(f"[Zadanie 15] Odpowiedź B: {response_b.decode('utf-8', errors='replace')}")
	except ConnectionResetError:
		print("[Zadanie 15] Brak działającego serwera UDP na wskazanym porcie (WinError 10054).")
	except OSError as error:
		print(f"[Zadanie 15] Błąd połączenia/komunikacji: {error}")


def task_16() -> None:
	print("[Zadanie 16] Brak implementacji.")


def main() -> None:
	task_handlers: dict[int, Callable[[], None]] = {
		13: task_13,
		14: task_14,
		15: task_15,
		16: task_16,
	}

	any_task_enabled = False

	for task_number in range(13, 17):
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