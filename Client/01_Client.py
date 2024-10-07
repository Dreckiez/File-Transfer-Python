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
    fn = ''
    fs = ''
    i = line.rfind(' ', 0, len(line))
    
    fn = line[0:i]
    fs = line[i+1:]
    return fn,fs

def receive_file(fileName, file_size):
    interval = time.time()
    # start = time.time()
    bytes_num = 0

    f = open(fileName, "wb")

    while bytes_num < file_size:
        datachunk = Client.recv(1024)
        if not datachunk:
            break
        else:
            f.write(datachunk)
            bytes_num += len(datachunk)
            check = time.time()
            percentage = round((bytes_num*100)/file_size)
            if check - interval >= 5:
                interval = check
                print("\033[1A\033[KDownloading " + file_name + " .... " + str(percentage) + "%")
    # end = time.time()
    f.close()
    print("\033[1A\033[KDownload " + fileName + " Completed\n")
    # print("Total time: ", str(end - start))

directory = "output"
cwd = os.getcwd()
path = os.path.join(cwd, directory)
Server_IP = "192.168.1.39" # Change to Server IP
Server_Port = 9999
file_content = read_file("input.txt")
downloaded = []

Client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
Client.connect((Server_IP, Server_Port))
Server_Addr = socket.socket.getsockname(Client)
print("Connect to [%s:%s]\n" %Server_Addr)
alist = Client.recv(1024).decode('latin-1')
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
                Client.send(file.encode('latin-1'))
    
                try:
                    os.mkdir(path)
                except OSError:
                    pass

                os.chdir(path)

                tmp = Client.recv(1024).decode('latin-1')
                file_name, file_size =  string_handle(tmp)
                print("Starting to download", file_name)
                
                receive_file(file_name, int(float(file_size)))

                os.chdir(cwd)

    except KeyboardInterrupt:
        break
print("\nDisconnected from Server")
Client.close()