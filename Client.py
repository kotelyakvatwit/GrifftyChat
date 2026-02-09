"""
Simple TCP chat client.

Connects to a server on port 1313 and provides a minimal interactive client.
- Starts two daemon threads: one reads stdin and sends messages; the other prints
  messages received from the server.
Usage: run the script, enter server address when prompted, type messages to send,
type 'exit' to quit and 'help' for a short hint.
"""
import socket
import sys
import threading

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
active = True

def input_thread():
    """
    Read lines from stdin and send them to the server.

    Special commands:
    - 'exit' (case-insensitive): stop the client and trigger shutdown.
    - 'help' : print a short usage hint from the server.

    The function runs while the module-level `active` flag is True and
    ignores common I/O errors to allow a clean thread exit.
    """
    global active
    while active:
        try:
            msg = input()
            match msg.lower():
                case "exit":
                    active = False
                    break
                case "help":
                    print("Type messages to send to the server. Type 'exit' to quit. For server commands, prefix with '\\' (e.g. '\\help').")
                case _:
                    s.sendall(msg.encode())
        except (OSError, EOFError):
            break

def output_thread():
    """
    Receive messages from the server and print them to stdout.

    If the server closes the connection (recv returns an empty bytes object),
    the thread prints a notice, clears `active` and exits.
    """
    global active
    while True:
        try:
            data = s.recv(1024)
            if data == b"":
                print("\nServer closed the connection. Try again later.")
                active = False
                break
            print("<", data.decode(errors="replace"))
            print("> ", end="", flush=True)
        except OSError:
            break

def main():
    """
    Prompt for the server address, connect, and run the client threads.

    Starts the input and output threads as daemons and waits while `active` is True.
    Cleans up the socket on exit and handles KeyboardInterrupt for graceful shutdown.
    """
    global s
    server_address = str(input("Enter server address: "))
    try:
        s.connect((server_address, 1313))
    except ConnectionRefusedError:
        print("Could not connect to server. Make sure the server is running.")
        return
    print("Connected to server. Type messages to send. Type 'exit' to quit.")

    input_t = threading.Thread(target=input_thread, daemon=True)
    output_t = threading.Thread(target=output_thread, daemon=True)

    try:
        input_t.start()
        output_t.start()
        while active:
            input_t.join(0.5)
            output_t.join(0.5)
    except KeyboardInterrupt:
        print("Interrupted by user.")
    finally:
        print("Exiting.")
        try:
            s.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        try:
            s.close()
        except OSError:
            pass
        sys.exit(0)


if __name__ == "__main__":
    main()