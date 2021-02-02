from anytree import Node, RenderTree, NodeMixin
from math import floor
import json
import os


class DataNode(NodeMixin):
    def __init__(self, name, parent=None, children=None):
        super(DataNode, self).__init__()
        self.name = name
        self.parent = parent
        if children:
            self.children = children


files = {}
nodes = {}


# Root file class

class root_file():
    def __init__(self, name="data.dat", size=1000, track_size=100):
        self.name = name
        self.size = size
        self.track_size = track_size
        self.available_tracks = list(range(1, floor(size / track_size) + 1))
        self.used_tracks = []

    def create_file(self):
        self.f = open(self.name, 'wb')
        self.f.seek(self.size - 1)
        self.f.write(b"\0")
        self.f.close()

    def write_to_file(self, text):
        self.f = open(self.name, 'r+b')
        if self.available_tracks != []:
            self.f.seek((self.available_tracks[0] - 1) * self.track_size)
            self.f.write(text.encode('utf-8'))
            temp = self.available_tracks.pop(0)
            self.used_tracks.append(temp)

    def write_to_file_at(self, text, write_at, track_num):
        self.f = open(self.name, 'r+b')
        self.f.seek(((track_num - 1) * self.track_size) + write_at)
        self.f.write(text.encode('utf-8'))

    def read_from_file(self, track_list, bytes_on_tracks):
        output = ""
        f = open("data.dat", "rb")
        for t in track_list:
            f.seek((t - 1) * self.track_size)
            output += f.read(bytes_on_tracks[t]).decode('utf-8')
        f.close()
        return output.strip()

    def read_from_file_at(self, tracks, start_track, start_byte_position, size):
        remaining_bytes = size
        self.f = open("data.dat", "rb")
        content_to_read = ""
        bytes_to_read = 0
        for track in tracks:
            if track >= start_track:
                if remaining_bytes <= tracks[track]:
                    bytes_to_read = remaining_bytes
                else:
                    bytes_to_read = tracks[track]

                self.f.seek(((track - 1) * self.track_size) + start_byte_position)
                content_to_read += self.f.read(bytes_to_read).decode('utf-8')
                remaining_bytes -= bytes_to_read
        return content_to_read


root = root_file()
nodes["root"] = DataNode(root.name)


class FileObj():
    def __init__(self, name, mode, root_file=root):
        self.name = name
        self.mode = mode
        self.size = 0
        self.track = 0
        self.size_on_track = 0
        self.root_file = root_file
        self.file_tracks = []
        self.bytes_on_tracks = {}
        self.content = ""
        self.open = False

    def write_to_file(self, text, output_file):
        self.content += text
        self.root_file.write_to_file(text)
        track_num = self.root_file.used_tracks[-1]
        self.file_tracks.append(track_num)
        self.bytes_on_tracks[track_num] = len(text)
        self.size += len(text)
        nodes[track_num] = DataNode(track_num, parent=nodes[self.name])
        output_file.write("Data has been written to file!")

    def write_to_file_at(self, text, write_at=0):
        self.input_text = text
        self.content += self.input_text
        track_to_write = 0
        byte_counter = write_at
        if (write_at <= self.size):
            for key in self.bytes_on_tracks:
                if byte_counter < self.bytes_on_tracks[key]:
                    track_to_write = key
                    break
                else:
                    byte_counter -= self.bytes_on_tracks[key]
            self.root_file.write_to_file_at(self.input_text, byte_counter, track_to_write)
        else:
            self.write_to_file(text)

    def read_from_file(self):
        output = self.root_file.read_from_file(self.file_tracks, self.bytes_on_tracks)
        return output

    def track_finder(self, byte_position):
        track = 0
        byte_counter = byte_position
        for key in self.bytes_on_tracks:
            if byte_counter < self.bytes_on_tracks[key]:
                start_track = key
                break
            else:
                byte_counter -= self.bytes_on_tracks[key]
        return track, byte_counter

    def read_from_file_at(self, start, size, output_file):
        start_track, start_byte_counter = self.track_finder(start)
        read_content = self.root_file.read_from_file_at(self.bytes_on_tracks, start_track, start_byte_counter, size)
        return read_content

    def chDir(self, DirName,output_file):
        if DirName in nodes:
            children = nodes[self.name].children
            nodes[self.name].parent = None
            nodes[self.name] = DataNode(self.name, parent=nodes[DirName])
            nodes[self.name].children = children
        else:
            output_file.write("Given directory does not exist")

    def copy_within_file(self, start, size, target):
        content_to_copy = self.read_from_file_at(start, size)
        self.write_to_file_at(content_to_copy, write_at=start)


# Main required Functions
def open_file(fname,output_file, mode="r+w"):

    """ Modes: r = read, w = write, r+w = read and write (append) """
    files[fname] = FileObj(fname, mode,output_file)
    output_file.write("File has been opened!")
    return files[fname]


def create(fname,output_file, p=nodes["root"]):
    output_file.write("File has been created!")
    open_file(fname,  output_file)
    nodes[fname] = DataNode(files[fname].name, parent=p)


def delete(fname,output_file):
    nodes[fname].parent = None
    output_file.write("File has been deleted!")


def close(fname,output_file):
    files[fname].open = False
    output_file.write("File has been Closed!")


def show_memory_map(output_file):
    output_file.write("Showing Memory Map: ")
    for pre, fill, node in RenderTree(nodes["root"]):
        output_file.write("%s%s" % (pre, node.name))


def makeDir(fname, output_file):
    nodes[fname] = DataNode(files[fname].name, parent=nodes["root"])
    output_file.write("Directory has been created!")


def file_system(thread_id, decision, file_name='', input_text='',username=''):
    output_file = open('thread_output_no'+str(thread_id)+'.txt','w')
    # input_file = open('input_thread_no_'+str(thread_id),'r')
    if decision == 1:
        create(fname=file_name, output_file=output_file)
        output_file.write("File created!")
    elif decision == 2:
        if file_name in files.keys():
            delete(file_name, output_file)
            output_file.write("File deleted")
        else:
            output_file.write("File does not exist")
    elif decision == 3:
        if file_name in files.keys():
            user_based = open('user_based.json', 'r')
            overall = open('overall.json', 'r')
            user_based_record = json.load(user_based)
            overall_record = json.load(overall)
            if username  in user_based_record.keys and user_based_record[username]==5:
                output_file.write('No more files for particular user')
            else:
                if file_name in overall_record.keys and overall_record[file_name]==3:
                    output_file.write('no more users can open this file')
                else:
                    overall.close()
                    user_based.close()
                    user_based = open('user_based.json', 'w')
                    overall = open('overall.json', 'w')
                    if username not in user_based_record.keys:
                        user_based_record[username]=0
                    if file_name not in overall_record.keys:
                        overall_record[file_name]=0
                    overall_record[file_name]= overall_record[file_name]+1
                    user_based_record[username] = user_based_record[username]+1
                    json.dump(overall, overall_record)
                    json.dump(user_based, user_based_record)
            f = open_file(file_name, output_file)
            output_file.write("File opened")
        else:
            output_file.write("File does not exist")
    elif decision == 4:
        if file_name in files.keys():
            close(file_name, output_file)
            output_file.write("File closed")
        else:
            output_file.write("File does not exist")

    elif decision == 5:
        if file_name in files.keys():
            files[file_name].write_to_file(input_text, output_file)
            output_file.write("Given content written to file successfully!")
        else:
            output_file.write("File does not exist")

    elif decision == 6:
        if file_name in files.keys():
            output_file.write("Reading from the given file: ")
            output_file.write(files[file_name].read_from_file())
        else:
            output_file.write("File does not exist")

    elif decision == 7:
        show_memory_map(output_file)

    else:
        output_file.write("Invalid input")
