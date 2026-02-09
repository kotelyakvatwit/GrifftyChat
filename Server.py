import socket
import threading

active = True

clients_lock = threading.Lock()
clients = {}

def processInput():
    global active
    while True:
        cmd = input().strip()

        if cmd == "exit":
            active = False
            print("\n\nSocket closed, exiting input thread")
            break
        else:
            print("Unknown command:", cmd)


def parse_target(s: str):
    host, port_str = s.rsplit(":", 1)
    port = int(port_str)
    if not (1 <= port <= 65535):
        raise ValueError("port out of range")
    socket.getaddrinfo(host, port)
    return host, port

def findClient(host: str, port: int):
    with clients_lock:
        for c, _ in clients.values():
            try:
                peer_host, peer_port = c.getpeername()
                if peer_host == host and peer_port == port:
                    return c
            except OSError:
                continue
    raise ValueError(f"No client found with address {host}:{port}")






def handle_msg(msg: str, addr):
    msg = msg.strip()
    if not msg.startswith("\\"):
        return f"Echo: {msg}"

    parts = msg[1:].split(maxsplit=2)
    cmd = parts[0]
    arg = parts[1] if len(parts) > 1 else None
    mes = parts[2:] if len(parts) > 2 else None


    match cmd:
        case "help":
            return "Available commands:\n\\help - Show this help message\n\\send {ip:port} {msg} - Send to target\n\\list - List connected clients"
        case "list":
            print(clients_lock)
            print(clients)
            print(addr)
            with clients_lock:
                return "Connected clients:\n" + "\n".join(
                    f"{c.getpeername()} {"- user" if c.getpeername() == addr else ""}"  for t, (c, _) in clients.items()
                )
        case "send" if (arg and mes):
            try:
                host, port = parse_target(arg)
                conn = findClient(host, port)
                conn.sendall(f"[{addr}] {" ".join(mes)}".encode())
            except Exception as e:
                return f"Something went wrong: \n(error: {e})\n Usage: \\{{send ip:port}} {{message}}"
            return f"Message sent to {host}:{port}"
        case "send":
            return "Usage: \\send {ip:port} {message}"
        case _:
            return f"Unknown command: {msg}"













def processClient(conn, addr, stop_event):
    print("Processing client", addr)

    conn.settimeout(3.0)

    conn.sendall(b"Hi dear user. This is a simple echo server with some client to client communication capabilities. \n For commands type '\\help'")

    try:
        while not stop_event.is_set():
            try:
                data = conn.recv(1024)
                if not data:
                    break
                response = handle_msg(data.decode(), addr)
                conn.sendall(response.encode())
            except socket.timeout:
                continue
            except (ConnectionResetError, OSError):
                break
    finally:
        print("Closing connection with", addr)
        try:
            conn.close()
        except OSError:
            pass
        finally:
            with clients_lock:
                for t, (c, _) in list(clients.items()):
                    if c == conn:
                        del clients[t]
                        break

def get_local_ip():
    """Fetches the machine's local IP address."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_address = s.getsockname()[0]
        s.close()
        return ip_address
    except socket.error as e:
        return f"Error: {e}"


def main():
    global active

    print("Server is running on local address:", get_local_ip())
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("", 1313))
    s.listen(30)
    s.settimeout(5.0)

    threading.Thread(target=processInput, daemon=True).start()

    while active:
        try:
            conn, addr = s.accept()
            stop_event = threading.Event()
            t = threading.Thread(target=processClient, args=(conn, addr, stop_event))
            with clients_lock:
                clients[t] = (conn, stop_event)
            t.start()
        except socket.timeout:
            continue
        except OSError:
            break

    with clients_lock:
        items = list(clients.items())

    for t, (conn, stop_event) in items:
        stop_event.set()
        try:
            conn.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        try:
            conn.close()
        except OSError:
            pass

    for t, _ in items:
        t.join()

    print("Server stopped")

if __name__ == "__main__":
    main()
