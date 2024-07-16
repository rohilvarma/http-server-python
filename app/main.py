import os
import socket
import threading
from argparse import ArgumentParser


def get_accessed_endpoint(request_line: str) -> str:
    """
    Extracts the endpoint from the HTTP request line.

    :param request_line: The request line of HTTP request.
    :returns: Endpoint from the request line, will return an empty string if endpoint doesn't exist.
    :rtype: str
    """
    return request_line.split(" ")[1]

def get_http_status_message(http_code: int) -> str:
    """
    Get the status message for an HTTP Code.
    
    :param http_code: HTTP response code.
    :returns: HTTP response code mesage.
    :rtype: str
    """
    match http_code:
        case 200:
            return "OK"
        case 201:
            return "Created"
        case 404:
            return "Not Found"
        case _:
            return "HTTP Code not found"

def create_http_response(
    http_code: int, 
    headers: dict[str, str]={}, 
    data: str=""
) -> bytes:
    """
    Create the HTTP response.

    :param http_code: Response code for the request.
    :param headers: Response headers dictionary.
    :param data: Response data to be sent.
    :returns: An HTTP Response.
    :rtype: bytes
    """
    status_line = "HTTP/1.1 {} {}".format(http_code, get_http_status_message(http_code)).encode()
    response_headers = ["{}: {}".format(key, value).encode() + b"\r\n" for key, value in headers.items()]
    response_headers = b"".join(response_headers)
    response_body = data.encode()
    return b"\r\n".join([status_line, response_headers, response_body])

def is_valid_compressions(compression_scheme: str) -> bool:
    """
    Determine if a compression scheme is supported by the HTTP Server.
    
    :param compresson_scheme: Compression scheme sent in the request.
    :returns: Response if a compression scheme exists.
    :rtype: bool
    """
    _valid_schemes_set = {"gzip"}
    compression_scheme_set = set(compression_scheme.split(", "))
    return len(compression_scheme_set.intersection(_valid_schemes_set)) > 0

def http_response_get(
    endpoint: str, 
    headers: dict[str, str], 
    dir_name: str | None = None,
    body_data: str = ""
) -> bytes:
    """
    Determines the GET HTTP response based on the endpoint accessed.

    :param endpoint: The endpoint requested by HTTP.
    :param headers: Headers dictionary containing all headers from the request.
    :param dir_name: Directory name where request file should exist.
    :param body_data: Request data in the body.
    :returns: Byte response for the HTTP request.
    :rtype: bytes
    """
    if endpoint == "/" or endpoint == "/index.html":
        return create_http_response(200)
    elif endpoint.startswith("/echo"):
        if is_valid_compressions(headers.get("Accept-Encoding", "")):
            return create_http_response(
                http_code=200,
                headers={
                    "Content-Encoding": "gzip",
                    "Content-Type": "text/plain",
                },
            )
        
        return create_http_response(
            http_code=200,
            headers={
                "Content-Type": "text/plain",
                "Content-Length": str(len(endpoint[6:]))
            },
            data=endpoint[6:]
        )
    elif endpoint == "/user-agent":
        user_agent_value = headers["User-Agent"]
        return create_http_response(
            http_code=200,
            headers={
                "Content-Type": "text/plain",
                "Content-Length": str(len(user_agent_value))
            },
            data=user_agent_value
        )
    elif endpoint.startswith("/files") and dir_name is not None:
        file_name = endpoint[7:]
        file_path = os.path.join(dir_name, file_name)
        if os.path.isfile(file_path):
            file_content = ""
            with open(file_path, "r") as file:
                file_content = file.read()
            file.close()
            return create_http_response(
                http_code=200,
                headers={
                    "Content-Type": "application/octet-stream",
                    "Content-Length": str(len(file_content))
                },
                data=file_content
            )

    return create_http_response(404)

def http_response_post(
    endpoint: str, 
    dir_name: str | None,
    body_data: str
) -> bytes:
    """
    Determines the POST HTTP response based on the endpoint accessed.

    :param endpoint: The endpoint requested by HTTP.
    :param dir_name: Directory where the file is to be created.
    :param body_data: Data/content to be written on the new file.
    :returns: Byte response for the HTTP request.
    :rtype: bytes
    """
    if endpoint.startswith("/files") and dir_name is not None:
        file_name = endpoint[7:]
        file_path = os.path.join(dir_name, file_name)
        
        with open(file_path, "w") as fout:
            fout.write(body_data)
        fout.close()

        return create_http_response(http_code=201)
        
    return create_http_response(404)

def create_headers(request_list: list[str]) -> dict[str, str]:
    """
    Method to create a headers dictionary from the HTTP request.

    :param request_list: HTTP request split by CRLF, contains header and body.
    :returns: A headers dictionary.
    :rtype: dict[str, str]
    """
    header_keys = [
        "Host", "User-Agent", "Accept", "Content-Type", "Content-Length", "Accept-Encoding", "Content-Encoding"
    ]

    headers = {}
    for header in request_list:
        if ":" in header:
            key, value = header.split(": ")
            if key in header_keys:
                headers[key] = value

    return headers

def handle_clients(client_socket: socket.socket, dir_name: str | None) -> None:
    """
    Handle one instance of a client connection.

    :param client_socket: Individual client connection socket.
    :param dir_name: Path of the directory where we create a file.
    :returns: Void function, doesn't returns anything.
    :rtype: None
    """
    try:
        request = client_socket.recv(1024).decode()
        request_list = request.split("\r\n")
        
        http_request_method = request_list[0].split(" ")[0]
        endpoint = get_accessed_endpoint(request_list[0])

        headers = create_headers(request_list[1:])
        match http_request_method:
            case "GET":
                client_socket.send(http_response_get(endpoint, headers, dir_name))
            
            case "POST":
                client_socket.send(http_response_post(endpoint, dir_name, request_list[-1]))
            
            case _:
                raise ValueError("Unexpected HTTP Request method passed.")
        

    except Exception as e:
        print("Exception occured", e)

    finally:
        client_socket.close()
        print("Connection is closed!\n")

def main(directory: str | None) -> None:
    print("Logs from your program will appear here!")

    server_socket = socket.create_server(("localhost", 4221), reuse_port=True, backlog=3)

    while True:
        client_socket, client_addr = server_socket.accept()
        print("New client connected!")

        connection_handler = threading.Thread(target=handle_clients, args=(client_socket, directory))
        connection_handler.start()


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--directory", type=str)
    args = parser.parse_args()
    main(args.directory)
