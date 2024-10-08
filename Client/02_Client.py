import socket
import os
import time
import threading
import sys

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

def create_request_dict(fileName):
    file = open(fileName, "r")
    for line in file:
        line = line.rstrip('\n')
        name, prio = line.rsplit(' ', 1)
        if name in allowed_list:
            if not name in downloaded:
                request_dict[name] = prio
                downloaded.append(name)
    file.close()

def has_file_changed(fileName):
    global file_content
    while True:
        check_modified = read_file(fileName)
        if check_modified != file_content:
            file_content = check_modified
            create_request_dict(fileName)
        time.sleep(2)

def printProggress(progess_dict, prev_len):
    print("\033[F" * prev_len, end='')
    for prog in list(progess_dict.keys()):
        print("\033[K", end='')
        print(progess_dict[prog])

def string_handle(line):
    i = line.find('/', 0, len(line))
    size = line[i+1:]

    return int(size)

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

def init_connect(sock, run_event):
    global prev_len
    threading.Thread(target=has_file_changed, args=(request_file_path,), daemon=True).start()
    while run_event.is_set():
        if len(request_dict):
            while len(request_dict):
                for name in list(request_dict.keys()):
                    os.chdir(path)

                    sock.send((name+'/'+request_dict[name]+"<END>").encode('latin-1'))
                    ans = Receive(sock, 1024).decode('latin-1')
                    file_size = string_handle(ans)

                    sock.send("OK<END>".encode('latin-1'))

                    if request_dict[name] == "CRITICAL":
                        data_chunk = Receive(sock, 536870912)
                    elif request_dict[name] == "HIGH":
                        data_chunk = Receive(sock, 67108864)
                    elif request_dict[name] == "NORMAL":
                        data_chunk = Receive(sock, 8388608)

                    if data_chunk[-6:] == b"<DONE>":
                        progress_dict[name] = f"Download {name} Completed"
                        # print("Download %s Completed\n" %name)
                        del request_dict[name]
                    else:
                        f = open(name, '+ab')
                        f.seek(0)
                        data = f.read()
                        bytes_num = len(data + data_chunk)
                        percentage = round((bytes_num*100)/file_size)
                        
                        progress_dict[name] = f"Downloading {name} .... {percentage}%"
                        
                        # print("Downloading %s .... %s%%" %(name, percentage))
                        f.write(data_chunk)
                        f.close()
                    os.chdir(cwd)
                    printProggress(progress_dict, prev_len)
                    prev_len = len(progress_dict)
                    
                



directory = "output"
cwd = os.getcwd()
request_file_path = os.path.join(cwd, "input.txt")
path = os.path.join(cwd, directory)
Server_IP = "10.126.6.103" # Change it to the Server IP
Server_Port = 9999
file_content = read_file("input.txt")
request_dict = {}
progress_dict = {}
downloaded = []
prev_len = 0

Client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
Client.connect((Server_IP, Server_Port))
Server_Addr = socket.socket.getsockname(Client)
print("Connect to [%s:%s]\n" %Server_Addr)

try:
    os.mkdir(path)
except OSError:
    pass

alist = Receive(Client, 1024).decode('latin-1')
allowed_list = list(alist.split('/'))
print("Allowed to Download files:")
print_list(allowed_list)


run_event = threading.Event()
run_event.set()
Connect_Thread = threading.Thread(target = init_connect, args=(Client,run_event))
Connect_Thread.start()
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    Client.send("<BYE><END>".encode('latin-1'))
    run_event.clear()
    Connect_Thread.join()

print("\nDisconnected from Server")
Client.close()