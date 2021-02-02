import socket
import threading

from main import file_system

HOST = '192.168.10.9'  # My private Ip address
PORT = 1420  # Port to listen on (non-privileged ports are > 1023

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(5)
log_file = open('log_file.txt', 'w')
connection_no = 0
threads = {}
while True:
    conn, addr = s.accept()
    connection_no += 1
    with conn:
        log_file.write("Connection no: " + str(connection_no) + '\n' + 'Connected by' + str(addr) + '\n')
        all_data = ''
        while True:
            data = conn.recv(1024)
            all_data += data.decode()
            if not data:
                break

            stripped_data = all_data.split('|')
            print(stripped_data)
            log_file.write("User: " + stripped_data[0] + str('\n'))
            command = stripped_data[1]
            striped_command_lines = command.split(' ')
            if len(striped_command_lines) == 3:
                threads[str(connection_no)] = threading.Thread(target=file_system, args=(
                    connection_no, int(striped_command_lines[0]), striped_command_lines[1],
                    striped_command_lines[2]))
            elif len(striped_command_lines) == 2:
                threads[str(connection_no)] = threading.Thread(target=file_system,
                                                               args=(connection_no, int(striped_command_lines[0]),
                                                                     striped_command_lines[1]))
            elif len(striped_command_lines) == 1:
                threads[str(connection_no)] = threading.Thread(target=file_system,
                                                               args=(connection_no, int(striped_command_lines[0]),'','',stripped_data[0]))
            log_file.write('Command: ' + stripped_data[1])
            conn.send(all_data.encode())
            log_file.flush()
            break
