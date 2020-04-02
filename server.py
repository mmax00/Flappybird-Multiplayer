import socket
import threading
import time
import random
import sys

def send_to_all_clients(message,client=None):
    encoded_message = bytes(message,'utf-8')
    for j in range(len(client_list)):
        try:
            if client_list[j]!=client:
                print('[*] Sent:', message, ' to ', client_addr[j][0], ':', client_addr[j][1], sep='')
                client_list[j].sendall(encoded_message)
        except:
            print('[!] Cant find: ', client_addr[j][0], ':', client_addr[j][1], sep='')
            handle_disconnect(client_list[j])

def handle_disconnect(client):
    global number_of_clients,client_names,client_addr,client_list
    for counter in range(number_of_clients):
        if client == client_list[counter]:
            name = client_names[counter]
            client_addr.pop(counter)
            client_names.pop(counter)
            client_list.pop(counter)
            number_of_clients-=1
            dc_text = '/dc*' + name+'*'
            send_to_all_clients(dc_text)



def handle_client(client):
    global clients_pos,ready_players,game_state,number_of_clients,dead_players
    print('[*] Client thread started ID:',number_of_clients)
    id = number_of_clients
    number_of_clients += 1
    while True:
        try:
            data = client.recv(1024)
            data = data.decode()
            # if data[:2]=='/p':
            #     d=d[3:]
            #     print(d)
            #     clients_pos[id] = d
            # else:
            if data =='ready':
                ready_players+=1
                data = '/q*'+str(ready_players)+' of '+str(number_of_clients)
                if ready_players==number_of_clients:
                    dead_players = 0
                    send_to_all_clients(data)
                    time.sleep(1)
                    generate_pipes()
                    time.sleep(1)
                    for i in range(4):
                        data = '/q*' +str(i)
                        send_to_all_clients(data)
                        time.sleep(1)
                    game_state = '/s*play'
                    data = game_state

            if data == 'dead':
                dead_players+=1
                if dead_players==number_of_clients:
                    time.sleep(2)
                    ready_players=0
                    game_state = '/s*q'
                    data = game_state

            if data[:3]=='/nc':
                send_to_all_clients(data)
                data = '/q*' + str(ready_players) + ' of ' + str(number_of_clients)
            send_to_all_clients(data)
            print('[*] Recieved:',data,'from:',client_addr[id])

        except:
            print(sys.exc_info())
            print('[!] Client disconnected!')
            handle_disconnect(id)
            break

def generate_pipes():
    msg='/p*'
    for i in range(10):
        msg+=str(random.randint(300,550))+'*'
    send_to_all_clients(msg)


def first_handle(con,addr):
    global number_of_clients,client_names,client_addr,client_list

    name = con.recv(1024)   #waits for the client name
    name = name.decode()
    print('[*] Recieved name from client',name)
    con.sendall(bytes(game_state,'utf-8'))

    #sends the info about connected players
    for cn in client_names:
        info = '/nc*'+cn+'*'
        con.sendall(bytes(info,'utf-8'))

    #adds new client to lists
    client_list.append(con)
    client_addr.append(addr)
    client_names.append(name)

    #starts client communication thread
    client_thread = threading.Thread(target=handle_client,args=(con,))
    client_thread.start()

    #Notifys the other client that someone has connected
    notify_text = '/nc*'+name+'*'
    send_to_all_clients(notify_text,client_list[number_of_clients])


def sync_clients():
    global counter
    while True:
        try:
            for j in range(len(client_names)):
                msg ='/p*'+client_names[j]+'*'+str(clients_pos[j])
                send_to_all_clients(msg)
        except:
            print(sys.exc_info())

        time.sleep(1)

client_list = []
client_addr = []
client_names = []
clients_pos=[0 for j in range(5)]
number_of_clients = 0
game_state='q'

ready_players = 0
dead_players=0

HOST = input("Enter host ip:")
PORT = 65432
NUMBER_of_CONCURENT_CLIENTS = 5

srv_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
srv_socket.bind((HOST,PORT))
print('[*] Server started at: ',HOST,':',str(PORT),sep='')

srv_socket.listen(NUMBER_of_CONCURENT_CLIENTS)

counter = 0
while True:
    conn,addr = srv_socket.accept()
    print('[*] Client connected from: ',addr[0],':',addr[1],sep='')
    first_handle(conn,addr)
    # sync_clients_thread = threading.Thread(target=sync_clients)
    # sync_clients_thread.start()



