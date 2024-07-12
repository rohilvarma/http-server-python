# Uncomment this to pass the first stage
import socket


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    _http_responses = {
        200: b"HTTP/1.1 200 OK\r\n\r\n",
        404: b"HTTP/1.1 404 Not Found\r\n\r\n"
    }
    _available_endpoints = [
        "", "index.html"
    ]

    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    while True:
        client_socket, client_address = server_socket.accept() # wait for client
        try:
            request = client_socket.recv(1024).decode('utf-8')
            print("Request received.")

            request_line = request.split('\r\n')[0]
            request_target = request_line.split(" ")[1].split("/")[1]
            print("Request Target is", '/'+(request_target))

            client_socket.sendall(_http_responses[200] if request_target in _available_endpoints else _http_responses[404])

        finally:
            client_socket.close()

if __name__ == "__main__":
    main()
