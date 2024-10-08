import socket
import os
import time
import threading


def print_list(ilist):
    for item in ilist:
        print("+ %s" %item)
    print('\n')

def read_file(fileName):
    file = open(fileName, "r")
    content = file.read()
    file.close()
    return content

def create_allow_list():
    file = open("list.txt", "r")
    for line in file:
        allowed_list.append(line.rstrip('\n'))
    file.close()


def string_handle(line):
    i = line.find('/', 0, len(line))
    
    file_name = line[0:i]
    prio = line[i+1:]

    return file_name, prio

def Receive(sock, buffer):
    data = b''
    check_len = 0
    while check_len < buffer:
        chunk = sock.recv(buffer)
        if not chunk:
            break
        else:
            check_len += len(chunk)
            data += chunk
    return data

    
def accept_connections():
    while True:
        Client, Client_Add = Server.accept()

        try:
            request_dict = {}
            print("Client connect from [%s:%s]" %Client_Add)
            Client.send(alist.join(allowed_list).encode('latin-1'))
            CThread = threading.Thread(target = handle_client, args = (Client,request_dict,Client_Add,))
            CThread.start()
        except not CThread.is_alive():
            Client.close()
        """ if not CThread.is_alive():
            Client.close()
            print("Client from %s:%s disconnected" %Client_Add) """

def handle_client(sock, request_dict, client_addr):
    while True:
        try:
            request = sock.recv(1024).decode('latin-1')
            file_name, prio = string_handle(request)
            print("[%s] requesting %s - %s" %(client_addr, file_name, prio))

            os.chdir(path)
            file_size = str(os.path.getsize(file_name))
            sock.send(file_size.encode('latin-1'))

            if file_name in request_dict:
                f_pos = request_dict[file_name]
            else:
                f_pos = 0

            
            f = open(file_name, "rb")
            f.seek(f_pos)
            
            if prio == "CRITICAL":
                data = f.read(536870912)
            elif prio == "HIGH":
                data = f.read(67108864)
            elif prio == "NORMAL":
                data = f.read(8388608)
            
            request_dict[file_name] = f.tell()

            f.close()

            ans = sock.recv(1024).decode('latin-1')
            
            if ans == "OK":
                os.chdir(cwd)
                if data:
                    sock.send(data)
                    print("SENT")
                else:
                    sock.send("<END>".encode('latin-1'))

        except OSError:
            print("[Client] from [%s:%s] disconnected" %client_addr)
            break

Server_IP = "0.0.0.0"
Server_Port = 9999
allowed_list = []
alist = '/'

# clients_addr = {}


directory = "files"
cwd = os.getcwd()
path = os.path.join(cwd, directory)

Server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
Server.bind((Server_IP, Server_Port))

Server.listen(5)
print("Waiting for Connection")

create_allow_list()

Accept_Thread = threading.Thread(target=accept_connections)
Accept_Thread.start()
Accept_Thread.join()
Server.close()
