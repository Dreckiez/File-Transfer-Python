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

def has_file_changed(fileName):
    global file_content
    check_modified = read_file(fileName)
    if check_modified != file_content:
        file_content = check_modified
        return True
    else: 
        return False

def print_file(fileName):
    content = read_file(fileName)
    print(content)

def send_file(fileName):
    data = read_file_in_binary(fileName)
    Client.sendall(data)

def create_request_list(fileName):
    file = open("input.txt", "r")
    for line in file:
        line = line.rstrip('\n')
        if line in allowed_list:
            if not line in downloaded:
                request_list.append(line)
                downloaded.append(line)
    file.close()

def string_handle(line):
    i = line.find('/', 0, len(line))
    
    fs = line[i+1:]
    return int(fs)

def receive_file(fileName, file_size):
    interval = time.time()
    # start = time.time()
    bytes_num = 0

    f = open(fileName, "wb")

    while bytes_num < file_size:
        datachunk = Client.recv(1024)
        if datachunk[-5:] == b"<END>":
            datachunk = datachunk[:len(datachunk) - 5]
            f.write(datachunk)
            break
        else:
            f.write(datachunk)
            bytes_num += len(datachunk)
            check = time.time()
            percentage = round((bytes_num*100)/file_size)
            if check - interval >= 5:
                interval = check
                print("\033[1A\033[KDownloading " + fileName + " .... " + str(percentage) + "%")
    # end = time.time()
    f.close()
    print("\033[1A\033[KDownload " + fileName + " Completed\n")
    # print("Total time: ", str(end - start))

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

directory = "output"
cwd = os.getcwd()
path = os.path.join(cwd, directory)
Server_IP = "10.126.6.103" # Change to Server IP
Server_Port = 9999
file_content = read_file("input.txt")
downloaded = []

Client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
Client.connect((Server_IP, Server_Port))
Server_Addr = socket.socket.getsockname(Client)
print("Connect to [%s:%s]\n" %Server_Addr)
alist = Receive(Client, 1024).decode('latin-1')
allowed_list = list(alist.split('/'))
print("Allowed to Download files:")
print_list(allowed_list)

while True:
    try:
        if has_file_changed("input.txt"):
            request_list = []
            create_request_list("input.txt")
            if len(request_list) != 0:
                print("New Request(s):")
                print_list(request_list)

            for file in request_list:
                Client.send((file+"<END>").encode('latin-1'))
    
                try:
                    os.mkdir(path)
                except OSError:
                    pass

                os.chdir(path)

                tmp = Receive(Client, 1024).decode('latin-1')
                file_size =  string_handle(tmp)
                print("Starting to download", file)
                
                receive_file(file, int(float(file_size)))

                os.chdir(cwd)

    except KeyboardInterrupt:
        Client.send("<BYE><END>".encode('latin-1'))
        break
print("\nDisconnected from Server")
Client.close()