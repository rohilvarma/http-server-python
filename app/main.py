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

def create_response(http_code: int, headers: dict[str, str]={}, data: str="") -> bytes:
    """
    Create the HTTP response.

    :param http_code: Response code for the request.
    :param headers: Response headers dictionary.
    :param data: Response data to be sent.
    :returns: An HTTP Response.
    :rtype: bytes
    """
    status_line = "HTTP/1.1 {} {}".format(http_code, "OK" if http_code == 200 else "Not Found").encode()
    response_headers = ["{}: {}".format(key, value).encode() + b"\r\n" for key, value in headers.items()]
    response_headers = b"".join(response_headers)
    response_body = data.encode()
    return b"\r\n".join([status_line, response_headers, response_body])

def get_http_response(endpoint: str, headers: dict[str, str], dir_name: str | None = None) -> bytes:
    """
    Determines the HTTP response based on the endpoint accessed.

    :param endpoint: The endpoint requested by HTTP.
    :param headers: Headers dictionary containing all headers from the request.
    :returns: Byte response for the HTTP request.
    :rtype: bytes
    """
    if endpoint == "/" or endpoint == "/index.html":
        return create_response(200)
    elif endpoint.startswith("/echo"):
        return create_response(
            http_code=200,
            headers={
                "Content-Type": "text/plain",
                "Content-Length": str(len(endpoint[6:]))
            },
            data=endpoint[6:]
        )
    elif endpoint == "/user-agent":
        user_agent_value = headers["User-Agent"]
        return create_response(
            http_code=200,
            headers={
                "Content-Type": "text/plain",
                "Content-Length": str(len(user_agent_value))
            },
            data=user_agent_value
        )
    elif endpoint.startswith("/files") and dir_name is not None:
        file_name = endpoint[7:]
        curr_dir = os.getcwd()
        file_path = os.path.join(dir_name, file_name)
        print(file_path)
        if os.path.isfile(file_path):
            file_content = ""
            with open(file_path, "r") as file:
                file_content = file.read()
            file.close()
            return create_response(
                http_code=200,
                headers={
                    "Content-Type": "application/octet-stream",
                    "Content-Length": str(len(file_content))
                },
                data=file_content
            )

    return create_response(404)

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

        endpoint = get_accessed_endpoint(request_list[0])

        headers = create_headers(request_list[1:])

        client_socket.send(get_http_response(endpoint, headers, dir_name))

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
