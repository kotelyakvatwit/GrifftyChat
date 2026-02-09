# GrifftyChat — Simple TCP Chat (Network Programming Lab)

This repository contains a small TCP-based chat server and client written in Python. It was created as a lab exercise for a network programming class to demonstrate basic socket programming, simple client-to-client messaging, and multithreading.

Files
- `Server.py` — TCP server that listens on port 1313, accepts clients, and supports a few simple commands (echo, list, send).
- `Client.py` — Minimal interactive client that connects to the server, sends typed messages, and prints server messages.

Requirements
- Python 3.10 or newer (the code uses structural pattern matching / `match` statements).
- No external dependencies (uses only Python's standard library).

Quick start
1. Open two terminals (or two machines on the same network).

2. Start the server in one terminal:

```bash
python3 Server.py
```

The server prints its local IP address and begins listening on port 1313. An operator can type `exit` in the server console to stop it gracefully.

3. Start the client in the other terminal:

```bash
python3 Client.py
```

Enter the server's IP address when prompted (for local testing you can use `127.0.0.1`).

Client usage
- Type regular text and press Enter to send a message to the server.
- Type `exit` to close the client.
- Type `help` to print a short usage hint.
- Server-side commands are prefixed with a backslash (for example, `\help`).

Server commands (from client)
- `\help` — shows available commands.
- `\list` — returns a list of connected clients.
- `\send ip:port message` — forwards `message` to a connected client identified by its peer address.

Server operator commands (server console)
- `exit` — shut down the server and all client connections.

Implementation notes
- Both server and client use threads: the client runs an input thread and an output thread; the server spawns a thread per client and a background thread to accept operator input.
- The server keeps a `clients` mapping protected by a lock; handlers use events to signal shutdown.
- The default port is 1313; change it in the source if you need a different port.

Troubleshooting
- If the client fails to connect, ensure the server is running and that the IP/port are reachable (firewall/NAT may block connections).
- Use `127.0.0.1` for local-only testing.
- The project requires Python 3.10+ because of `match` statements.

Possible improvements
- Add authentication or simple usernames.
- Replace blocking input() calls with a non-blocking or GUI-based client.
- Implement message framing to support binary data and longer messages.

License
This is a small educational lab project; apply your institution's preferred license or treat it as sample code for learning purposes.