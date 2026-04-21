from typing import Callable

from recvall import (
    ImapSession,
    connect_and_login,
)

# Globalnie uzywam:
# login: student@localhost
# haslo: test123

TASK1_HOST = "127.0.0.1"
TASK1_PORT = 1310
TASK1_EMAIL = "student@localhost"

TASK2_HOST = "127.0.0.1"
TASK2_PORT = 1311
TASK2_EMAIL = "student@localhost"

TASK3_HOST = "127.0.0.1"
TASK3_PORT = 1312
TASK3_EMAIL = "student@localhost"

TASK4_HOST = "127.0.0.1"
TASK4_PORT = 1313
TASK4_EMAIL = "student@localhost"

TASK5_HOST = "127.0.0.1"
TASK5_PORT = 1314
TASK5_EMAIL = "student@localhost"

TASK6_HOST = "127.0.0.1"
TASK6_PORT = 1315
TASK6_EMAIL = "student@localhost"

TASK_TOGGLES: dict[int, bool] = {
    1: True,
    2: True,
    3: True,
    4: True,
    5: True,
    6: False,
}


def task_1() -> None:
    print(f"[zad1] IMAP mailbox survey -> {TASK1_HOST}:{TASK1_PORT}")
    email = input(f"[zad1] Login [{TASK1_EMAIL}]: ").strip() or TASK1_EMAIL
    password = input("[zad1] Haslo: ").strip()
    if not password:
        print("[zad1] Haslo jest wymagane.")
        return

    try:
        session = connect_and_login(TASK1_HOST, TASK1_PORT, email, password, "zad1")
        mailboxes = session.list_mailboxes()
        print("[zad1] Skrzynki:")
        for mailbox in mailboxes:
            messages, unseen = session.status(mailbox)
            print(f"[zad1] {mailbox}: {messages} wiadomosci, {unseen} nieprzeczytanych")

        inbox_count, _ = session.status("INBOX")
        print(f"[zad1] Inbox ma {inbox_count} wiadomosci")

        session.select_mailbox("INBOX")
        available = session.search("ALL")
        if not available:
            print("[zad1] Inbox jest pusty.")
        else:
            first_seq = available[0]
            print(f"[zad1] Pierwsza dostepna wiadomosc: {first_seq}")
            session.fetch_message(first_seq)
            session.store_flags(first_seq, "+FLAGS", r"\Seen")
            print(f"[zad1] Wiadomosc {first_seq} oznaczona jako przeczytana.")

        session.logout()
    except (OSError, RuntimeError, TimeoutError) as error:
        print(f"[zad1] Error: {error}")


def task_2() -> None:
    print(f"[zad2] IMAP Inbox count -> {TASK2_HOST}:{TASK2_PORT}")
    email = input(f"[zad2] Login [{TASK2_EMAIL}]: ").strip() or TASK2_EMAIL
    password = input("[zad2] Haslo: ").strip()
    if not password:
        print("[zad2] Haslo jest wymagane.")
        return

    try:
        session = connect_and_login(TASK2_HOST, TASK2_PORT, email, password, "zad2")
        messages, unseen = session.status("INBOX")
        print(f"[zad2] Inbox: {messages} wiadomosci, {unseen} nieprzeczytanych")
        session.logout()
    except (OSError, RuntimeError, TimeoutError) as error:
        print(f"[zad2] Error: {error}")


def task_3() -> None:
    print(f"[zad3] IMAP total mailbox count -> {TASK3_HOST}:{TASK3_PORT}")
    email = input(f"[zad3] Login [{TASK3_EMAIL}]: ").strip() or TASK3_EMAIL
    password = input("[zad3] Haslo: ").strip()
    if not password:
        print("[zad3] Haslo jest wymagane.")
        return

    try:
        session = connect_and_login(TASK3_HOST, TASK3_PORT, email, password, "zad3")
        total_messages = 0
        for mailbox in session.list_mailboxes():
            messages, unseen = session.status(mailbox)
            total_messages += messages
            print(f"[zad3] {mailbox}: {messages} wiadomosci, {unseen} nieprzeczytanych")

        print(f"[zad3] Razem we wszystkich skrzynkach: {total_messages}")
        session.logout()
    except (OSError, RuntimeError, TimeoutError) as error:
        print(f"[zad3] Error: {error}")


def task_4() -> None:
    print(f"[zad4] IMAP unread review -> {TASK4_HOST}:{TASK4_PORT}")
    email = input(f"[zad4] Login [{TASK4_EMAIL}]: ").strip() or TASK4_EMAIL
    password = input("[zad4] Haslo: ").strip()
    if not password:
        print("[zad4] Haslo jest wymagane.")
        return

    try:
        session = connect_and_login(TASK4_HOST, TASK4_PORT, email, password, "zad4")
        session.select_mailbox("INBOX")
        unread = session.search("UNSEEN")
        if not unread:
            print("[zad4] Brak nieprzeczytanych wiadomosci.")
        else:
            print(f"[zad4] Nieprzeczytane: {', '.join(str(item) for item in unread)}")
            for seq in unread:
                body = session.fetch_message(seq)
                print(f"[zad4] --- WIADOMOSC {seq} ---")
                print(body.rstrip())
                session.store_flags(seq, "+FLAGS", r"\Seen")
                print(f"[zad4] Wiadomosc {seq} oznaczona jako przeczytana.")

        session.logout()
    except (OSError, RuntimeError, TimeoutError) as error:
        print(f"[zad4] Error: {error}")


def task_5() -> None:
    print(f"[zad5] IMAP delete chosen message -> {TASK5_HOST}:{TASK5_PORT}")
    email = input(f"[zad5] Login [{TASK5_EMAIL}]: ").strip() or TASK5_EMAIL
    password = input("[zad5] Haslo: ").strip()
    if not password:
        print("[zad5] Haslo jest wymagane.")
        return

    try:
        session = connect_and_login(TASK5_HOST, TASK5_PORT, email, password, "zad5")
        session.select_mailbox("INBOX")
        all_messages = session.search("ALL")
        if not all_messages:
            print("[zad5] Inbox jest pusty.")
            session.logout()
            return

        print(f"[zad5] Dostepne wiadomosci: {', '.join(str(item) for item in all_messages)}")
        chosen = input("[zad5] Ktora wiadomosc usunac? ").strip()
        try:
            seq = int(chosen)
        except ValueError:
            print("[zad5] Niepoprawny numer wiadomosci.")
            session.logout()
            return

        if seq not in all_messages:
            print("[zad5] Taka wiadomosc nie istnieje.")
            session.logout()
            return

        session.store_flags(seq, "+FLAGS", r"\Deleted")
        session.expunge()
        print(f"[zad5] Wiadomosc {seq} usunieta fizycznie.")
        session.logout()
    except (OSError, RuntimeError, TimeoutError) as error:
        print(f"[zad5] Error: {error}")


def task_6() -> None:
    print(f"[zad6] IMAP unsupported command demo -> {TASK6_HOST}:{TASK6_PORT}")
    email = input(f"[zad6] Login [{TASK6_EMAIL}]: ").strip() or TASK6_EMAIL
    password = input("[zad6] Haslo: ").strip()
    if not password:
        print("[zad6] Haslo jest wymagane.")
        return

    try:
        session = connect_and_login(TASK6_HOST, TASK6_PORT, email, password, "zad6")
        session.select_mailbox("INBOX")
        response = session.command_allow_failure("X-UNKNOWN-COMMAND")
        final_line = response[-1] if response else ""
        print(f"[zad6] Odpowiedz na nieznana komende: {final_line}")
        if final_line.startswith("A") and "NO" in final_line:
            print("[zad6] OK: serwer poprawnie pokazal obsluge niezaimplementowanej komendy.")
        session.logout()
    except (OSError, RuntimeError, TimeoutError) as error:
        print(f"[zad6] Error: {error}")


def main() -> None:
    task_handlers: dict[int, Callable[[], None]] = {
        1: task_1,
        2: task_2,
        3: task_3,
        4: task_4,
        5: task_5,
        6: task_6,
    }

    any_task_enabled = False
    for task_number in range(1, 7):
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
