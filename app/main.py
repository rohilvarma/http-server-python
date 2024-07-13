import socket
import threading


def get_accessed_endpoint(request_line: str) -> str:
    """
    Extracts the endpoint from the HTTP request line.
    
    :param request_line: The request line of HTTP request.
    :returns: Endpoint from the request line, will return an empty string if endpoint doesn't exist.
    :rtype: str
    """
    return request_line.split(" ")[1]
    
def get_http_response(endpoint: str, headers: dict[str, str]) -> bytes:
    """
    Determines the HTTP response based on the endpoint accessed.
    
    :param endpoint: The endpoint requested by HTTP.
    :param headers: Headers dictionary containing all headers from the request.
    :returns: Byte response for the HTTP request.
    :rtype: bytes
    """
    if endpoint == "/" or endpoint == "/index.html":
        return b"HTTP/1.1 200 OK\r\n\r\n"
    elif endpoint.startswith("/echo"):
        response = "HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {}\r\n\r\n{}".format(len(endpoint[6:]), endpoint[6:])
        return response.encode()
    elif endpoint == "/user-agent":
        user_agent_value = headers["User-Agent"]
        response = "HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {}\r\n\r\n{}".format(len(user_agent_value), user_agent_value)
        return response.encode()
    
    return b"HTTP/1.1 404 Not Found\r\n\r\n"
    
def create_headers(request_list: list[str]) -> dict[str, str]:
    """
    Method to create a headers dictionary from the HTTP request.
    
    :param request_list: HTTP request split by CRLF, contains header and body.
    :returns: A headers dictionary.
    :rtype: dict[str, str]
    """
    header_keys = ["Host", "User-Agent", "Accept"]
    
    headers = {}
    for header in request_list:
        if ":" in header:
            key, value = header.split(": ")
            if key in header_keys:
                headers[key] = value
                
    return headers

def handle_clients(client_socket: socket.socket):
    try:
        request = client_socket.recv(1024).decode()
        request_list = request.split("\r\n")
        
        endpoint = get_accessed_endpoint(request_list[0])
        
        headers = create_headers(request_list[1:])
        
        client_socket.send(get_http_response(endpoint, headers))
        
    except Exception as e:
        print("Exception occured", e)

    finally:
        client_socket.close()
        print("Connection is closed!\n")

def main() -> None:
    print("Logs from your program will appear here!")
    
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True, backlog=3)
    
    while True:
        client_socket, client_addr = server_socket.accept()
        print("New client connected!")
        
        connection_handler = threading.Thread(target=handle_clients, args=(client_socket, ))
        connection_handler.start()

    
if __name__ == "__main__":
    main()
