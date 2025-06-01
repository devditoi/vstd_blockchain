import socket

# Create a relay server socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('localhost', 12345))
server_socket.listen(1)

while True:
    # Accept incoming connections
    client_socket, client_address = server_socket.accept()

    # Receive data from the client
    data = client_socket.recv(1024)

    print(data)

    # Send the received data back to the client
    client_socket.send(data)

    # Close the client socket
    client_socket.close()