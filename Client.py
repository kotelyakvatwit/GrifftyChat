import socket
import sys
import threading

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
active = True

def input_thread():
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
    global s
    server_address = str(input("Enter server address: "))
    try:
        s.connect((server_address, 1313))
    except ConnectionRefusedError:
        print("Could not connect to server. Make sure the server is running.")
        return
    print("Connected to server. Type messages to send. Type 'exit' to quit.")

    input_T = threading.Thread(target=input_thread, daemon=True)
    output_T = threading.Thread(target=output_thread, daemon=True)

    try:
        input_T.start()
        output_T.start()
        while active:
            input_T.join(0.5)
            output_T.join(0.5)
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
