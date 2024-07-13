import socket

def get_accessed_endpoint(request_line: str) -> str:
    return request_line.split(" ")[1]
    
def get_http_response(endpoint: str, headers: dict[str, str]) -> bytes:
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
    header_keys = ["Host", "User-Agent", "Accept"]
    
    headers = {}
    for header in request_list:
        if ":" in header:
            key, value = header.split(": ")
            if key in header_keys:
                headers[key] = value
                
    return headers

def main() -> None:
    print("Logs from your program will appear here!")
    
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    
    while True:
        client_socket, client_addr = server_socket.accept()
        print("New client connected!")
        
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
    
    
if __name__ == "__main__":
    main()