from socket import *
import sys
import os
import time

# Abrindo um socket UDP e setando o ip, porta e número de bytes do buffer
socket_client = socket(AF_INET, SOCK_DGRAM)
client_ip = gethostbyname(gethostname())
client_port = 4455
server_ip = client_ip # pois a troca de pacotes está acontecendo no mesmo IP
server_port = 6789
buffer_size = 1024
server_ip_port_tuple = (server_ip, server_port)


###### Etapa 1: Enviando o arquivo ######

print("======= Envio do arquivo ========")

file_name = sys.argv[1]
f = open('./' + file_name, 'rb')    # Abrindo um arquivo

file_size = os.path.getsize(file_name)

# Enviando o nome do arquivo para o servidor
socket_client.sendto(file_name.encode(), server_ip_port_tuple)
socket_client.sendto(str(file_size).encode(), server_ip_port_tuple)


state = 0
sequence_number = 0
# Enviando pacotes de 1024 em 1024 bytes para o servidor, até que o arquivo seja completamente enviado
file_data = f.read(buffer_size-1)                 # Lendo os primeiros *buffer_size* bytes do arquivo
cnt = 1
while(file_data != b''):

    if(state == 0): 
        file_data = b'0' + file_data

        if(socket_client.sendto(file_data, server_ip_port_tuple)):
            receiver_pkt = None
            state = 1

    if(state == 1):

        try:
            socket_client.settimeout(0.2)
            receiver_pkt, receiver_ip_port_tuple = socket_client.recvfrom(buffer_size) 
        except timeout:
            print("Retransmissão necessária")
            socket_client.sendto(file_data, server_ip_port_tuple)
        
        if receiver_pkt is not None:
            if receiver_pkt[:1] == b'0':
                state = 2
                file_data = f.read(buffer_size-1)
                if file_data == b'':
                    break
        # elif(receiver_pkt.decode()[0] == '1'): 
        #     socket_client.sendto(file_data, server_ip_port_tuple)


    if(state == 2):

        file_data = b'1' + file_data

        if(socket_client.sendto(file_data, server_ip_port_tuple)):
            receiver_pkt = None
            state = 3

    if(state == 3):

        try:
            socket_client.settimeout(0.2)
            receiver_pkt, receiver_ip_port_tuple = socket_client.recvfrom(buffer_size) 
        except timeout:
            print("Retransmissão necessária")
            socket_client.sendto(file_data, server_ip_port_tuple)
        
        if receiver_pkt is not None: 
            if receiver_pkt[:1] == b'1':
                state = 0
                file_data = f.read(buffer_size-1)
                if file_data == b'':
                    break
        #elif(receiver_pkt.decode()[0] == '0'): 
        #    socket_client.sendto(file_data, server_ip_port_tuple)



print("Fim do envio do arquivo")

f.close()
socket_client.close()

