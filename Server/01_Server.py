import socket
import os
import time

def print_list(ilist):
    for item in ilist:
        print("+ %s" %item)
    print('\n')

def read_file_in_binary(fileName):
    file = open(fileName, "rb")
    data = file.read()
    file.close()
    return data

def read_file(fileName):
    file = open(fileName, "r")
    content = file.read()
    file.close()
    return content

def send_file(fileName):
    data = read_file_in_binary(fileName)
    data += b'<ENDF>'
    Client.sendall(data)

def create_allow_list():
    file = open("list.txt", "r")
    for line in file:
        allowed_list.append(line.rstrip('\n'))
    file.close()

def Receive(sock, buffer):
    data = b''
    check_len = 0
    while check_len < buffer:
        chunk = sock.recv(buffer)
        if chunk[-5:] == b"<END>":
            chunk = chunk[:len(chunk) - 5]
            data += chunk
            break
        else:
            check_len += len(chunk)
            data += chunk
    return data

Server_IP = "0.0.0.0"
Server_Port = 9999
allowed_list = []
downloaded = []


directory = "files"
cwd = os.getcwd()
path = os.path.join(cwd, directory)

Server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
Server.bind((Server_IP, Server_Port))

Server.listen(1)
print("Waiting for Connection\n")
create_allow_list()

alist = '/'


while True:
    Client, Client_Add = Server.accept()
    try:
        print("Client connect from [%s:%s]\n" %Client_Add)

        
        Client.send((alist.join(allowed_list)+"<END>").encode('latin-1'))

        print("Allowed to Download files:")
        print_list(allowed_list)
        

        #HANDLE A CLIENT
        done = False
        while not done:
            file_name = Receive(Client, 1024).decode('latin-1')
            if not file_name or file_name == "<BYE>":
                done = True
            else:
                print("[Client] requesting " + file_name)


            os.chdir(path)

            file_size = str(os.path.getsize(file_name))
            Client.send((file_size+"<END>").encode('latin-1'))

            print("Sending " + file_name + '\n')              
            send_file(file_name)
            
            os.chdir(cwd)

    except OSError:
        Client.close()
        print("[Client] from [%s:%s] disconnected\n" %Client_Add)
    if Client is None:
        break

Server.close()
print("Server closed")