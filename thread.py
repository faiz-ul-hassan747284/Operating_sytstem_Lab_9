import threading

from main import file_system

k = int(input("Enter the number of threads: "))
input_file_name = input("Enter the input file name: ")
input_file = open(input_file_name, 'r')
command_lines = input_file.readlines()
striped_command_lines = []
for command_line in command_lines:
    striped_command_lines.append(command_line.split(' '))
print("After the threads are executed look for thread output in the same folder")
threads = {}
for x in range(k):
    if len(striped_command_lines) == 3:
        threads[str(x)] = threading.Thread(target=file_system, args=(
            x, int(striped_command_lines[0][0]), striped_command_lines[0][1], striped_command_lines[0][2]))
    elif len(striped_command_lines) == 2:
        threads[str(x)] = threading.Thread(target=file_system,
                                           args=(x, int(striped_command_lines[0][0]), striped_command_lines[0][1]))
    elif len(striped_command_lines) == 1:
        threads[str(x)] = threading.Thread(target=file_system, args=(x, int(striped_command_lines[0][0])))
for x in range(k):
    threads[str(x)].start()
