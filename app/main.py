import socket
import re


def check_endpoints(endpoint: str) -> tuple[bool, str]:
    _available_endpoints = [
        "/", "/index.html", "/echo"
    ]
    echo_route_value = re.split(_available_endpoints[2], endpoint)
    return endpoint in _available_endpoints or echo_route_value[0] == '', echo_route_value[1] if len(echo_route_value)>1 else ""
    
def main():
    print("Logs from your program will appear here!")

    _http_responses = {
        200: b"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: 3\r\n\r\n",
        404: b"HTTP/1.1 404 Not Found\r\n\r\n"
    }
    
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    while True:
        client_socket, client_address = server_socket.accept() # wait for client
        try:
            request = client_socket.recv(1024).decode('utf-8')
            print("Request received.")
            
            # Extracting the Request line of the HTTP request.
            request_line = request.split('\r\n')[0]
            
            # Extracting the request target value of the HTTP request.
            request_target = request_line.split(" ")[1]
            
            request_available, route_path = check_endpoints(request_target)
            
            log_message = "Request Target is" if request_available else "Invalid Request Target."
            print(log_message, request_target)
            print("$$$$$$$$$$$$$$")
            
            if request_available:
                if route_path != "":
                    # Taking from 1 index to omit the '/'
                    client_socket.send(_http_responses[200] + route_path[1:].encode())
                else:
                    client_socket.send(_http_responses[200])
            else:
                client_socket.send(_http_responses[404])
            client_socket.send(_http_responses[200] if request_available else _http_responses[404])

        except Exception as e:
            print("Error encountered", e)
            
        # client_socket.close()    
        # print("Connection closed!")

if __name__ == "__main__":
    main()
    # a, b = check_endpoints('/echo/abc')
    # print(a, b)
